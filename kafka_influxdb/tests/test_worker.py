import unittest
from mock import Mock
import random
import time
from kafka_influxdb.worker import Worker
from kafka_influxdb.encoder import echo_encoder
from kafka_influxdb.tests.helpers.timeout import timeout
from requests.exceptions import ConnectionError
from influxdb.exceptions import InfluxDBServerError, InfluxDBClientError


class Config:
    """
    Dummy config with minimum settings to pass the tests
    """
    def __init__(self, buffer_size, buffer_timeout):
        self.buffer_size = buffer_size
        self.buffer_timeout = buffer_timeout
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

class TimeoutReader(object):
    """
    A reader that writes half the messages then times out
    """
    def __init__(self, message, num_messages, timeout):
        self.message = message
        self.num_messages = num_messages
        self.timeout = timeout

    def read(self):
        for i in range(self.num_messages-1):
            yield self.message
        # Simulate no additional messages causing timeout
        time.sleep(self.timeout)
        yield False
        # Stop consuming
        raise SystemExit

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
        self.config = Config(10, 0.1)
        self.encoder = echo_encoder.Encoder()
        self.writer = Mock()
        self.writer.write.return_value = True

    def test_create_database(self):
        """
        Retry creating the InfluxDB database in case of a connection error
        """
        reader = DummyReader(["bar"], self.config.buffer_size)
        writer_with_connection_error = Mock()
        writer_with_connection_error.create_database = Mock(side_effect=[ConnectionError, None])

        client = Worker(reader, self.encoder, writer_with_connection_error, self.config)
        client.consume()
        self.assertEqual(writer_with_connection_error.create_database.call_count, 2)

    def test_flush(self):
        """
        Messages should be flushed to the writer when the buffer is full.
        """
        reader = DummyReader(["bar"], self.config.buffer_size)
        client = Worker(reader, self.encoder, self.writer, self.config)
        client.consume()
        self.assertTrue(self.writer.write.called)
        self.writer.write.assert_called_once_with(["bar"] * self.config.buffer_size)

    def test_buffer_timeout(self):
        """
        If the buffer has timed out flush to the writer.
        """
        reader = TimeoutReader("bar", self.config.buffer_size, self.config.buffer_timeout)
        client = Worker(reader, self.encoder, self.writer, self.config)
        client.consume()
        self.assertTrue(self.writer.write.called)
        self.writer.write.assert_called_once_with(["bar"] * int(self.config.buffer_size-1))

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
