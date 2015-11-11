import unittest
from mock import Mock
import random
from kafka_influxdb.worker import Worker
from kafka_influxdb.encoder import echo_encoder


class Config:
    def __init__(self, buffer_size):
        self.buffer_size = buffer_size
        self.kafka_topic = "test"
        self.influxdb_dbname = "mydb"


class DummyReader(object):
    """
    A reader that yields dummy messages
    """
    def __init__(self, messages, num_messages):
        self.messages = messages
        self.num_messages = num_messages

    def read(self):
        for i in range(self.num_messages):
            yield random.choice(self.messages)


class FlakyReader(object):
    """
    A fake reader that throws exceptions to simulate
    connection errors
    """
    def __init__(self, message, num_messages):
        self.message = message
        self.num_messages = num_messages

    def read(self):
        # Yield the first half of messages
        for i in range(int(self.num_messages/2)):
            yield self.message
        # Simulate a connection error while reading
        try:
            raise Exception
        except Exception:
            # Continue like you don't care.
            # Yield the second half of messages
            for i in range(int(self.num_messages/2)):
                yield self.message

class DummyWriter(object):
    """
    A fake writer that does nothing with the input data
    """
    def __init__(self):
        pass

    def write(self):
        pass


class TestKafkaInfluxDB(unittest.TestCase):
    def setUp(self):
        self.config = Config(100)
        self.encoder = echo_encoder.Encoder()
        self.writer = DummyWriter()
        self.writer = Mock()
        self.writer.write.return_value = True

    def test_buffering(self):
        self.reader = DummyReader(["foo"], self.config.buffer_size - 1)
        self.client = Worker(self.reader, self.encoder, self.writer, self.config)
        self.client.consume()
        self.assertFalse(self.writer.write.called)

    def test_flush(self):
        self.reader = DummyReader(["bar"], self.config.buffer_size)
        self.client = Worker(self.reader, self.encoder, self.writer, self.config)
        self.client.consume()
        self.assertTrue(self.writer.write.called)

    def test_reconnect(self):
        self.reader = FlakyReader(["baz"], self.config.buffer_size)
        self.client = Worker(self.reader, self.encoder, self.writer, self.config)
        self.client.consume()
        self.assertTrue(self.writer.write.called)
        self.writer.write.assert_called_once_with(["baz"] * self.config.buffer_size)
