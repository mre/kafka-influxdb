# -*- coding: utf-8 -*-

import logging
from kafka import KafkaConsumer
from kafka.common import ConsumerTimeout

from kafka_influxdb.encoder.errors import EncoderError


class Reader(object):
    """
    A Kafka consumer based on kafka-python
    See: https://github.com/dpkp/kafka-python
    """
    def __init__(self, host, port, group, topic):
        """
        Initialize Kafka reader
        """
        self.host = host
        self.port = port
        self.group = group
        self.topic = topic

        # Initialized on read
        self.consumer = None

    def _connect(self):
        connection = "{0}:{1}".format(self.host, self.port)
        logging.info("Connecting to Kafka at %s...", connection)
        self.consumer = KafkaConsumer(self.topic,
                                      group_id=self.group,
                                      bootstrap_servers=[connection])

    def read(self):
        """
        Read from Kafka. Reconnect on error.
        """
        for msg in self._handle_read():
            yield msg

    def _handle_read(self):
        """
        Yield messages from Kafka topic
        """
        try:
            self._connect()
            for message in self.consumer:
                yield message.value
        except ConsumerTimeout as timeout:
            logging.error("Kafka error: %s.", timeout)
            # The actual reconnect handling is done in the worker
            raise EncoderError(timeout.message)
