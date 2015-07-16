# -*- coding: utf-8 -*-

import logging
import time
from kafka.client import KafkaClient
from kafka.consumer import SimpleConsumer

class KafkaReader(object):

    def __init__(self, host, port, group, topic, connection_wait_time=2):
        """ Initialize Kafka reader """
        self.host = host
        self.port = port
        self.group = group
        self.topic = topic
        self.connection_wait_time = connection_wait_time

    def connect(self):
        connection = "{0}:{1}".format(self.host, self.port)
        logging.info("Connecting to Kafka at {}...", connection)
        self.kafka_client = KafkaClient(connection)
        self.consumer = SimpleConsumer(self.kafka_client,
                                       self.group,
                                       self.topic)

    def read(self):
        """ Yield messages from Kafka topic """
        while True:
            try:
                self.connect()
                for raw_message in self.consumer:
                    yield raw_message.message.value
            except Exception:
                logging.error("Connection to Kafka lost. Trying to reconnect to {}:{}...",
                                    self.host, self.port)
                time.sleep(self.connection_wait_time)
