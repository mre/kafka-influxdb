import logging
import time


class Worker(object):
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
        Run loop. Consume messages from reader, convert it to the output format and write with writer
        """
        self.init_database()

        logging.info("Listening for messages on Kafka topic %s...", self.config.kafka_topic)
        self.start_time = time.time()
        try:
            for index, raw_message in enumerate(self.reader.read(), 1):
                self.buffer.extend(self.encoder.encode(raw_message))
                if index % self.config.buffer_size == 0:
                    self.flush()
        except KeyboardInterrupt:
            logging.info("Shutdown")

    def init_database(self):
        """
        Initialize the InfluxDB database if it is not already there
        """
        try:
            logging.info("Creating InfluxDB database if not exists: %s", self.config.influxdb_dbname)
            self.writer.create_database(self.config.influxdb_dbname)
        except Exception as e:
            logging.info(e)

    def flush(self):
        """ Flush values with writer """
        try:
            self.writer.write(self.buffer)
            if self.config.statistics:
                self.show_statistics()
        except Exception as e:
            logging.warning(e)
        self.buffer = []

    def show_statistics(self):
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
