# -*- coding: utf-8 -*-

import logging
from kafka.client import KafkaClient
from kafka.consumer import SimpleConsumer

class KafkaReader(object):

    def __init__(self, host, port, group, topic):
        """ Initialize Kafka reader """
        connection = "{0}:{1}".format(host, port)
        logging.info("Connecting to Kafka at %s...", connection)
        kafka_client = KafkaClient(connection)
        self.consumer = SimpleConsumer(kafka_client, group, topic)

    def read(self):
        """ Yield messages from Kafka topic """
        for raw_message in self.consumer:
            yield raw_message.message.value
