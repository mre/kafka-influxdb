import unittest
import mock
import pytest

confluent = pytest.importorskip('kafka_influxdb.reader.confluent')


class KafkaError(object):
    def __init__(self):
        """
        Error types raised by confluent kafka
        """
        self._PARTITION_EOF = 1


class TestConfluentKafka(unittest.TestCase):
    def setUp(self):
        self.host = "myhost"
        self.port = 1234
        self.group = "mygroup"
        self.topic = "mytopic"
        self.reconnect_wait_time = 0.01
        self.reader = self.create_reader()

    def create_reader(self):
        reader = confluent.Reader(self.host,
                                  self.port,
                                  self.group,
                                  self.topic)
        reader.consumer = mock.MagicMock()
        return reader

    @staticmethod
    def create_kafka_message(key, value, kafka_error_type=None):
        message = mock.MagicMock()
        message.return_value = True
        message.key.return_value = key
        message.value.return_value = value
        if kafka_error_type:
            message.error.return_value = True
            message.error.code.return_value = kafka_error_type
        else:
            message.error.return_value = False
        return message

    def sample_messages(self, payload, count):
        message = self.create_kafka_message(None, payload)
        return count * [message], count * [payload]

    def test_handle_read(self):
        sample_messages, extracted_messages = self.sample_messages("hello", 3)
        self.reader.consumer.poll.side_effect = sample_messages
        self.reader._connect = mock.MagicMock()
        received_messages = list(self.reader._handle_read())
        self.assertEqual(received_messages, extracted_messages)

    def receive_messages(self):
        for message in self.reader.read():
            yield message
