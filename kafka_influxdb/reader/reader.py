import logging
from kafka_influxdb.encoder.errors import EncoderError


class ReaderAbstract(object):
    """
    A Kafka consumer based on kafka-python
    See: https://github.com/dpkp/kafka-python
    """

    # We need to treat legacy Kafka Versions (< 0.9.0) a little different.
    # First, they don't work without Zookeeper and confluent-kafka has no support for Zookeeper.
    # Second, they don't support API discovery.
    # The specific workarounds required are documented below.
    KAFKA_VERSION_ZOOKEEPER_OPTIONAL = "0.9.0"

    def __init__(self, host, port, group, topic, broker_version=KAFKA_VERSION_ZOOKEEPER_OPTIONAL):
        """
        Initialize Kafka reader
        """
        self.host = host
        self.port = str(port)
        self.group = group
        self.topic = topic
        self.broker_version = broker_version

        # Initialized on read
        self.consumer = None

    def read(self):
        """
        Read from Kafka. Reconnect on error.
        """
        try:
            self._connect()
            for msg in self._handle_read():
                yield msg
        finally:
            logging.info("Performing cleanup before stopping.")
            self._shutdown()

    def _connect(self):
        """
        Overwrite in child classes
        """
        raise NotImplementedError

    def _shutdown(self):
        """
        Cleanup tasks (e.g. closing the Kafka connection).
        Can be overwritten by specific readers if required.
        """
        if self.consumer:
            self.consumer.close()

    def _handle_read(self):
        """
        Read messages from Kafka.
        Library-specific internal message handling.
        Needs to be implemented by every reader
        """
        raise NotImplementedError
