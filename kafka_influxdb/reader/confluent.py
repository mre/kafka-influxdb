# -*- coding: utf-8 -*-

import logging
from confluent_kafka import Consumer, KafkaError, KafkaException, TopicPartition
from kafka_influxdb.encoder.errors import EncoderError


class Reader(object):
    """
    A high-performance Kafka consumer based on confluent-kafka, which uses librdkafka internally.
    See: https://github.com/confluentinc/confluent-kafka-python
    """

    # We need to treat legacy Kafka Versions (< 0.9.0) a little different.
    # First, they don't work without Zookeeper and confluent-kafka has no support for Zookeeper.
    # Second, they don't support API discovery.
    # The specific workarounds required are documented below.
    KAFKA_VERSION_ZOOKEEPER_OPTIONAL = "0.9.0"

    def __init__(self, host, port, group, topic, broker_version=None):
        """
        Initialize Kafka reader
        """
        self.host = host
        self.port = str(port)
        self.group = group
        self.topic = [topic]
        self.broker_version = broker_version

        # Initialized on read
        self.consumer = None

    @staticmethod
    def _on_assign(consumer, partitions):
        """
        Callback called on partition assignment to consumer
        """
        logging.debug('Consumer %s: Partitions assigned: %s', consumer, partitions)

    def _subscribe(self):
        if self.broker_version >= self.KAFKA_VERSION_ZOOKEEPER_OPTIONAL:
            self.consumer.subscribe(self.topic, on_assign=self._on_assign)
        else:
            # A workaround for missing Zookeeper support in confluent-python.
            # Automatic partition rebalancing is not working with Kafka Versions < 0.9.0.
            # Therefore we manually assign the partitions to the consumer for legacy Kafka versions.
            self.consumer.assign([TopicPartition(self.topic) for partition in range(0, 20)])

    def _setup_connection(self):
        connection = {
            'bootstrap.servers': self.host + ":" + self.port,
            'group.id': self.group,
            'session.timeout.ms': 6000,
            'default.topic.config': {
                'auto.offset.reset': 'largest'
            }
        }
        # Add additional flag based on the Kafka version.
        if self.broker_version < self.KAFKA_VERSION_ZOOKEEPER_OPTIONAL:
            connection['broker.version.fallback'] = self.broker_version

        return connection

    def _connect(self):
        connection = self._setup_connection()
        logging.info("Connecting to Kafka at %s...", connection)
        self.consumer = Consumer(**connection)

    def read(self):
        """
        Read from Kafka. Reconnect on error.
        """
        for msg in self._handle_read():
            yield msg

    def _handle_read(self):
        """
        Read from Kafka. Reconnect on error.
        """
        try:
            self._connect()
            while True:
                msg = self.consumer.poll(timeout=1.0)
                if msg is None:
                    continue
                if msg.error():
                    # Error or event
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        # End of partition event
                        logging.info('%s [%d] reached end at offset %d with key %s\n',
                                     msg.topic(), msg.partition(), msg.offset(), str(msg.key()))
                    else:
                        raise EncoderError(msg.error())
                else:
                    # Proper message
                    logging.debug('%s [%d] at offset %d with key %s:\n',
                                  msg.topic(), msg.partition(), msg.offset(), str(msg.key()))
                    # TODO: Is this still needed?
                    # otherwise the # writer will add extra \n
                    # self.buffer.append(msg.value().rstrip('\n'))
                    # TODO: What about commit handling? self.consumer.commit(async=False)
                    yield msg.value()
        except KeyboardInterrupt:
            logging.info('Aborted by user\n')
        # Close down consumer to commit final offsets.
        self.consumer.close()
        yield self.buffer
