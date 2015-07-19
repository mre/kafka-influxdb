import unittest
import mock
import itertools
from collections import namedtuple
from kafka_influxdb.reader import kafka_reader
from kafka.client import KafkaClient
from kafka.common import ConnectionError
from kafka.common import Message
from kafka_influxdb.tests.helpers.timeout import timeout

class TestKafkaReader(unittest.TestCase):

    def setUp(self):
        self.host = "myhost",
        self.port = 1234
        self.group = "mygroup"
        self.topic = "mytopic"
        self.reconnect_wait_time = 0.01

        self.reader = kafka_reader.KafkaReader(self.host,
                                                self.port,
                                                self.group,
                                                self.topic,
                                                self.reconnect_wait_time)
        self.reader.connect = mock.MagicMock()
        self.reader.consumer = mock.MagicMock()

    def sample_messages(self, payload, count):
        RawMessage = namedtuple('RawMessage', 'message')
        return (count * [RawMessage(message=Message(0, 0, None, payload))], count * [payload])

    def test_handle_read(self):
        sample_messages, extracted_messages = self.sample_messages("hello", 3)
        self.reader.consumer.__iter__.return_value = sample_messages
        received_messages = list(self.reader.handle_read())
        self.assertEquals(received_messages, extracted_messages)

    @timeout(0.1)
    def test_reconnect(self):
        """
        In case of a connection error, the client should reconnect and
        start receiving messages again without interruption
        """
        sample_messages1, extracted_messages1 = self.sample_messages("hi", 3)
        sample_messages2, extracted_messages2 = self.sample_messages("world", 3)
        sample_messages = sample_messages1 + [ConnectionError] + sample_messages2
        self.reader.consumer.__iter__.return_value = sample_messages
        received_messages = list(self.receive_messages())
        self.assertEquals(received_messages, extracted_messages1 + extracted_messages2)

    def receive_messages(self):
        for message in self.reader.read():
            yield message
