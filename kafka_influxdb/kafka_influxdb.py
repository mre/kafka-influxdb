import sys
import logging
import time
from config import loader
from encoder import load_encoder
from reader import kafka_reader
from writer import influxdb_writer
from writer import kafka_sample_writer as benchmark

class KafkaInfluxDB(object):
    def __init__(self, reader, encoder, writer, config):
        """
        Setup
        """
        self.config = config
        self.reader = reader
        self.encoder = encoder
        self.writer = writer
        self.buffer = []

    def consume(self):
        """
        Run loop. Consume messages from reader, convert it to the output format and write with writer
        """
        self.init_database()

        logging.info("Listening for messages on Kafka topic %s...", self.config.kafka_topic)
        self.start_time = time.time()
        try:
            for index, raw_message in enumerate(self.reader.read(), 1):
                self.buffer.append(self.encoder.encode(raw_message))
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
        logging.info("Flushing output buffer. {0:.2f} messages/s".format(msg_per_sec))
        # Reset timer
        self.start_time = time.time()

    def set_reader(self, reader):
        self.reader = reader

    def get_reader(self):
        self.reader = reader

    def set_writer(self, writer):
        self.writer = writer

    def get_writer(self):
        self.writer = writer

    def get_buffer(self):
        return self.buffer

    def get_config(self):
        return self.config

def create_sample_messages(config):
    print("Starting in benchmark mode. Stand by while creating sample messages.")
    logging.info("Writing sample messages for benchmark to topic %s", config.kafka_topic)
    bench = benchmark.KafkaSampleWriter(config)
    bench.produce_messages()

def main():
    """
    Setup consumer
    """
    config = loader.load_config()
    logging.info("Connecting to Kafka broker at %s:%s", config.kafka_host, config.kafka_port)
    if config.benchmark:
        create_sample_messages(config)
    start_consumer(config)

def start_consumer(config):
    """
    Start metrics consumer
    """
    try:
        reader = kafka_reader.KafkaReader(config.kafka_host,
                                        config.kafka_port,
                                        config.kafka_group,
                                        config.kafka_topic)
    except Exception as e:
        logging.error("The connection to Kafka can not be established: %s. Please check your config.", e.message)
        sys.exit(-1)

    encoder = load_encoder(config.encoder)

    logging.info("Connecting to InfluxDB at %s:%s", config.influxdb_host, config.influxdb_port)
    try:
        writer = influxdb_writer.InfluxDBWriter(config.influxdb_host,
                                        config.influxdb_port,
                                        config.influxdb_user,
                                        config.influxdb_password,
                                        config.influxdb_dbname,
                                        config.influxdb_use_ssl,
                                        config.influxdb_verify_ssl,
                                        config.influxdb_timeout,
                                        config.influxdb_use_udp,
                                        config.influxdb_retention_policy,
                                        config.influxdb_time_precision)
    except Exception as e:
        logging.error("The connection to InfluxDB can not be established: %s", e.message)
        sys.exit(-2)

    client = KafkaInfluxDB(reader, encoder, writer, config)
    client.consume()

if __name__ == '__main__'	:
    main()
