import unittest
import mock
from kafka_influxdb.reader import kafka_python
from kafka.common import Message


class TestKafkaPython(unittest.TestCase):
    def setUp(self):
        self.host = "myhost"
        self.port = 1234
        self.group = "mygroup"
        self.topic = "mytopic"
        self.reconnect_wait_time = 0.01
        self.reader = self.create_reader()

    def create_reader(self):
        reader = kafka_python.Reader(self.host,
                                     self.port,
                                     self.group,
                                     self.topic)
        reader.consumer = mock.MagicMock()
        return reader

    def sample_messages(self, payload, count):
        return count * [Message(0, 0, None, payload)], count * [payload]

    def test_handle_read(self):
        sample_messages, extracted_messages = self.sample_messages("hello", 3)
        self.reader.consumer.__iter__.return_value = sample_messages
        self.reader._connect = mock.MagicMock()
        received_messages = list(self.reader._handle_read())
        self.assertEqual(received_messages, extracted_messages)

    def receive_messages(self):
        for message in self.reader.read():
            yield message
