import logging
from confluent_kafka import Consumer, KafkaError, KafkaException, TopicPartition
from kafka_influxdb.encoder.errors import EncoderError
from kafka_influxdb.reader.reader import ReaderAbstract


class Reader(ReaderAbstract):
    """
    A high-performance Kafka consumer based on confluent-kafka, which uses librdkafka internally.
    See: https://github.com/confluentinc/confluent-kafka-python
    """

    def _subscribe(self):
        """
        Subscribe to Kafka topics.

        A workaround for missing Zookeeper support in confluent-python is required here.
        Automatic partition rebalancing is not working with Kafka Versions < 0.9.0.
        Therefore we manually assign the partitions to the consumer for legacy Kafka versions.
        """
        if self.broker_version < self.KAFKA_VERSION_ZOOKEEPER_OPTIONAL:
            self.consumer.assign([TopicPartition(self.topic, p) for p in range(0, 10)])
        else:
            self.consumer.subscribe([self.topic])

    def _setup_connection(self):
        """
        Confluent-Kafka configuration
        """
        # TODO: Test async commit handling (self.consumer.commit(async=False))
        connection = {
            'bootstrap.servers': self.host + ":" + self.port,
            'group.id': self.group,
            'offset.store.method': 'broker',
            'default.topic.config': {
                # TODO: Make this configurable
                'auto.offset.reset': 'largest'  # smallest
            }
        }
        # Add additional flag based on the Kafka version.
        if self.broker_version < self.KAFKA_VERSION_ZOOKEEPER_OPTIONAL:
            connection['broker.version.fallback'] = self.broker_version

        return connection

    def _connect(self):
        """
        Connect to Kafka and subscribe to the topic
        """
        connection = self._setup_connection()
        logging.info("Connecting to Kafka with the following settings:\n %s...", connection)
        self.consumer = Consumer(**connection)
        self._subscribe()

    def _handle_read(self):
        """
        Read messages from Kafka.
        """
        while True:
            msg = self.consumer.poll(timeout=1.0)
            if __debug__:
                logging.debug(msg)
            if msg is None:
                yield False
                continue
            if msg.error():
                self._handle_error(msg)
            else:
                # Proper message
                if __debug__:
                    logging.debug('%s [%d] at offset %d with key %s:\n',
                                  msg.topic(), msg.partition(), msg.offset(), str(msg.key()))
                yield msg.value().rstrip()

    @staticmethod
    def _handle_error(msg):
        if not msg.error():
            return
        # Error or event
        if msg.error().code() == KafkaError._PARTITION_EOF:
            # End of partition event
            logging.info('%s [%d] reached end at offset %d with key %s\n',
                         msg.topic(), msg.partition(), msg.offset(), str(msg.key()))
        else:
            raise EncoderError(msg.error())
