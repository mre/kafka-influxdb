# -*- coding: utf-8 -*-

import logging
import time
from kafka.client import KafkaClient
from kafka.consumer import SimpleConsumer

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

    def connect(self):
        connection = "{0}:{1}".format(self.host, self.port)
        logging.info("Connecting to Kafka at %s...", connection)
        self.kafka_client = KafkaClient(connection)
        self.consumer = SimpleConsumer(self.kafka_client,
                                       self.group,
                                       self.topic)

    def read(self):
        """
        Read from Kafka. Reconnect on error.
        """
        while True:
            for msg in self.handle_read():
                yield msg

    def handle_read(self):
        """
        Yield messages from Kafka topic
        """
        try:
            self.connect()
            for raw_message in self.consumer:
                yield raw_message.message.value
        except Exception as e:
            logging.error("Kafka error: %s.", e.message)
            logging.error("Trying to reconnect to %s:%s", self.host, self.port)
            time.sleep(self.reconnect_wait_time)
            pass
