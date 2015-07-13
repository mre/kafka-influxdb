import sys
from collections import defaultdict
import argparse
import yaml
import logging
import importlib
from reader import kafka_reader
from writer import influxdb_writer
from writer import kafka_sample_writer as benchmark
import six

import traceback
import time

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

        self.start_time = time.time()
        logging.info("Listening for messages on Kafka topic %s...", self.config.kafka_topic)
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
        print("Flushing output buffer. {0:.2f} messages/s".format(msg_per_sec))
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

def main():
    """
    Setup consumer
    """
    config = parse_args()

    # Set verbosity level
    if config.verbose == 1:
        logging.getLogger().setLevel(logging.INFO)
    elif config.verbose > 1:
        logging.getLogger().setLevel(logging.DEBUG)

    if config.configfile:
        logging.debug("Reading config from ", config.configfile)
        values = parse_configfile(config.configfile)
        overwrite_config_values(config, values)
    else:
        logging.info("Using default configuration")

    if config.benchmark:
        logging.info("Writing sample messages for benchmark")
        bench = benchmark.KafkaSampleWriter(config)
        bench.produce_messages()

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
        logging.error("The connection to Kafka can not be established.")
        sys.exit(-1)

    encoder = load_encoder(config.encoder)
    writer = influxdb_writer.InfluxDBWriter(config.influxdb_host,
                                    config.influxdb_port,
                                    config.influxdb_user,
                                    config.influxdb_password,
                                    config.influxdb_dbname,
                                    config.influxdb_retention_policy,
                                    config.influxdb_time_precision)

    client = KafkaInfluxDB(reader, encoder, writer, config)
    client.consume()

def load_encoder(encoder_name):
    """
    Creates an instance of the given encoder.
    An encoder converts a message from one format to another
    """
    encoder_module = importlib.import_module("encoder." + encoder_name)
    encoder_class = getattr(encoder_module, "Encoder")
    # Return an instance of the class
    return encoder_class()

def parse_configfile(configfile):
    """
    Read settings from file
    """
    with open(configfile) as f:
        try:
            return yaml.safe_load(f)
        except Exception as e :
            logging.fatal("Could not load default config file: ", e)
            exit(-1)

def overwrite_config_values(config, values, prefix = ""):
    """
    Overwrite default config with custom values
    """
    for key, value in six.iteritems(values):
        if type(value) == type(dict()):
            overwrite_config_values(config, value, "%s_" % key)
        elif value != '':
            setattr(config, "%s%s" % (prefix, key), value)

def parse_args():
    parser = argparse.ArgumentParser(description='A Kafka consumer for InfluxDB', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # Parameters
    parser.add_argument('--kafka_host', type=str, default='localhost', required=False, help="Hostname or IP of Kafka message broker")
    parser.add_argument('--kafka_port', type=int, default=9092, required=False, help="Port of Kafka message broker")
    parser.add_argument('--kafka_topic', type=str, default='my_topic', required=False, help="Topic for metrics")
    parser.add_argument('--kafka_group', type=str, default='my_group', required=False, help="Kafka consumer group")
    parser.add_argument('--influxdb_host', type=str, default='localhost', required=False, help="InfluxDB hostname or IP")
    parser.add_argument('--influxdb_port', type=int, default=8086, required=False, help="InfluxDB API port")
    parser.add_argument('--influxdb_user', type=str, default='root', required=False, help="InfluxDB username")
    parser.add_argument('--influxdb_password', type=str, default='root', required=False, help="InfluxDB password")
    parser.add_argument('--influxdb_dbname', type=str, default='metrics', required=False, help="InfluXDB database to write metrics into")
    parser.add_argument('--influxdb_retention_policy', type=str, default='default', required=False, help="Retention policy for incoming metrics")
    parser.add_argument('--influxdb_time_precision', type=str, default="s", required=False, help="Precision of incoming metrics. Can be one of 's', 'm', 'ms', 'u'")
    parser.add_argument('--encoder', type=str, default='collectd_graphite_encoder', required=False, help="Input encoder which converts an incoming message to dictionary")
    parser.add_argument('--buffer_size', type=int, default=1000, required=False, help="Maximum number of messages that will be collected before flushing to the backend")
    parser.add_argument('-c', '--configfile', type=str, default=None, required=False, help="Configfile path")
    # Flags
    parser.add_argument('-s', '--statistics', default=True, action="store_true", help="Show performance statistics")
    parser.add_argument('-b', '--benchmark', default=False, action="store_true", help="Run benchmark")
    parser.add_argument('-v', '--verbose', action='count', default=0, help="Set verbosity level. Increase verbosity by adding a v: -v -vv -vvv")
    return parser.parse_args()

if __name__ == '__main__'	:
    main()
