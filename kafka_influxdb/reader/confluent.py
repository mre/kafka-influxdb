# -*- coding: utf-8 -*-

import logging
from confluent_kafka import Consumer, KafkaError, KafkaException
from kafka_influxdb.encoder.errors import EncoderError


class Reader(object):
    """
    A high-performance Kafka consumer based on confluent-kafka, which uses librdkafka internally.
    See: https://github.com/confluentinc/confluent-kafka-python
    """
    def __init__(self, host, port, group, topic, buffer_size=1000):
        """
        Initialize Kafka reader
        """
        self.host = host
        self.port = str(port)
        self.group = group
        self.topic = [topic]
        self.buffer_size = buffer_size
        self.buffer = []

        # Initialized on read
        self.consumer = None

    @staticmethod
    def _on_assign(consumer, partitions):
        """
        Callback called on partition assignment to consumer
        """
        logging.debug('Consumer %s: Partitions assigned: %s', consumer, partitions)

    def _connect(self):
        connection = {
            'bootstrap.servers': self.host + ":" + self.port,
            'group.id': self.group,
            'session.timeout.ms': 6000,
            'default.topic.config': {
                'auto.offset.reset': 'largest'
            }
        }
        logging.info("Connecting to Kafka at %s...", connection)
        self.consumer = Consumer(**connection)
        self.consumer.subscribe(self.topic, on_assign=self._on_assign)

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
