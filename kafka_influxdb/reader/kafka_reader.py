# -*- coding: utf-8 -*-

import logging
import time
from kafka import KafkaConsumer


class KafkaReader(object):
    def __init__(self, host, port, group, topic, reconnect_wait_time=2):
        """
        Initialize Kafka reader
        """
        self.host = host
        self.port = port
        self.group = group
        self.topic = topic
        self.reconnect_wait_time = reconnect_wait_time

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
        while True:
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
        except Exception as e:
            logging.error("Kafka error: %s.", e)
            logging.error("Trying to reconnect to %s:%s", self.host, self.port)
            time.sleep(self.reconnect_wait_time)
            pass
