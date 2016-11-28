# -*- coding: utf-8 -*-
import logging
from kafka import KafkaConsumer
from kafka.common import ConsumerTimeout, KafkaUnavailableError

from kafka_influxdb.encoder.errors import EncoderError
from kafka_influxdb.reader.reader import ReaderAbstract


class Reader(ReaderAbstract):
    """
    A Kafka consumer based on kafka-python
    See: https://github.com/dpkp/kafka-python
    """

    def _connect(self):
        connection = "{0}:{1}".format(self.host, self.port)
        logging.info("Connecting to Kafka at %s...", connection)
        try:
            self.consumer = KafkaConsumer(self.topic,
                                          group_id=self.group,
                                          bootstrap_servers=[connection]
                                          )
        except KafkaUnavailableError as e:
            raise EncoderError(e)

    def _handle_read(self):
        """
        Read messages from Kafka.
        """
        try:
            for message in self.consumer:
                yield message.value
        except ConsumerTimeout as timeout:
            logging.error("Kafka error: %s.", timeout)
            # The actual reconnect handling is done in the caller
            raise EncoderError(timeout)
