import unittest
from mock import Mock
import random
from kafka_influxdb.worker import Worker
from kafka_influxdb.encoder import echo_encoder
from kafka_influxdb.tests.helpers.timeout import timeout
from kafka.common import ConnectionError


class Config:
    """
    Dummy config with minimum settings to pass the tests
    """
    def __init__(self, buffer_size):
        self.buffer_size = buffer_size
        self.kafka_topic = "test"
        self.influxdb_dbname = "mydb"
        self.statistics = False


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
        # Simulate keyboard interrupt by user to stop consuming
        raise KeyboardInterrupt


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
        # Simulate keyboard interrupt by user to stop consuming
        raise KeyboardInterrupt


class TestWorker(unittest.TestCase):
    """
    Tests for message worker.
    """
    def setUp(self):
        self.config = Config(10)
        self.encoder = echo_encoder.Encoder()
        self.writer = Mock()
        self.writer.write.return_value = True

    def test_flush(self):
        """
        Messages should be flushed to the writer when the buffer is full.
        """
        reader = DummyReader(["bar"], self.config.buffer_size)
        client = Worker(reader, self.encoder, self.writer, self.config)
        client.consume()
        self.assertTrue(self.writer.write.called)
        self.writer.write.assert_called_once_with(["bar"] * self.config.buffer_size)

    @timeout(0.1)
    def test_reconnect(self):
        """
        The worker should reconnect when the connection is interrupted.
        """
        reader = FlakyReader("baz", self.config.buffer_size)
        client = Worker(reader, self.encoder, self.writer, self.config)
        client.consume()
        self.assertTrue(self.writer.write.called)
        self.writer.write.assert_called_once_with(["baz"] * self.config.buffer_size)
