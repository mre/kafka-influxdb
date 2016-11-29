"""
A worker handles the connection to both, Kafka and InfluxDB and handles encoding in between.
"""
import logging
import time
import sys
from requests.exceptions import ConnectionError
from influxdb.exceptions import InfluxDBServerError, InfluxDBClientError
from kafka_influxdb.encoder.errors import EncoderError


class Worker(object):
    """
    Implementation of worker class that handles Kafka and InfluxDB
    connections and manages message encoding.
    """
    def __init__(self, reader, encoder, writer, config):
        """
        Setup
        """
        self.config = config
        self.reader = reader
        self.encoder = encoder
        self.writer = writer
        self.buffer = []

        # Field for time measurement
        self.start_time = None

    def consume(self):
        """
        Run loop. Consume messages from reader, convert it to the
        output format using encoder and write to output with writer
        """
        self.init_database()

        logging.info("Listening for messages on Kafka topic %s...", self.config.kafka_topic)
        self.start_time = time.time()
        while True:
            try:
                for index, raw_message in enumerate(self.reader.read(), 1):
                    self.buffer.extend(self.encoder.encode(raw_message))
                    if index % self.config.buffer_size == 0:
                        self.flush()
            except EncoderError:
                logging.error("Encoder error. Trying to reconnect to %s:%s",
                              self.config.kafka_host, self.config.kafka_port)
                logging.debug("Sleeping for %d ms before reconnect",
                              self.config.reconnect_wait_time_ms)
                time.sleep(self.config.reconnect_wait_time_ms / 1000.0)
            except KeyboardInterrupt:
                logging.info("Shutdown. Flushing remaining messages from buffer.")
                self.flush()
                break

    def init_database(self):
        """
        Initialize the InfluxDB database if it is not already there
        """
        try:
            logging.info("Creating InfluxDB database if not exists: %s",
                         self.config.influxdb_dbname)
            self.writer.create_database(self.config.influxdb_dbname)
        except (ConnectionError, InfluxDBServerError, InfluxDBClientError) as error:
            logging.error("Error while creating InfluxDB datbase: %s", error)
            sys.exit(2)

    def flush(self):
        """
        Flush values with writer
        """
        if not self.buffer:
            # Don't do anything when buffer empty
            return
        try:
            self.writer.write(self.buffer)
            if self.config.statistics:
                self.show_statistics()
        except (InfluxDBServerError, InfluxDBClientError) as influx_error:
            logging.error("Error while writing to InfluxDB: %s", influx_error)
        finally:
            self.buffer = []

    def show_statistics(self):
        """
        Print performance metrics to stdout
        """
        delta = time.time() - self.start_time
        msg_per_sec = self.config.buffer_size / delta
        print("Flushing output buffer. {0:.2f} messages/s".format(msg_per_sec))
        # Reset timer
        self.start_time = time.time()

    def set_reader(self, reader):
        self.reader = reader

    def get_reader(self):
        return self.reader

    def set_writer(self, writer):
        self.writer = writer

    def get_writer(self):
        return self.writer

    def get_buffer(self):
        return self.buffer

    def get_config(self):
        return self.config
