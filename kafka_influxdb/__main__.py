import sys
import logging
from .worker import Worker
from kafka_influxdb.writer import kafka_sample_writer, influxdb_writer
from kafka_influxdb.encoder import load_encoder
from kafka_influxdb.reader import kafka_reader
from kafka_influxdb.config import loader

__title__ = 'kafka_influxdb'
__author__ = 'Matthias Endler'
__license__ = 'Apache License 2.0'
__copyright__ = 'Copyright 2015, Matthias Endler under Apache License, v2.0'


def create_sample_messages(config):
    logging.info("Writing sample messages for benchmark to topic: '%s'", config.kafka_topic)
    benchmark = kafka_sample_writer.KafkaSampleWriter(config.kafka_host, config.kafka_port, config.kafka_topic)
    benchmark.produce_messages()


def main():
    """
    Setup consumer
    """
    config = loader.load_config()
    if config.version:
        show_version()
    if config.benchmark:
        print("Starting in benchmark mode. Stand by while creating sample messages.")
        create_sample_messages(config)
    start_consumer(config)

def show_version():
    from .version import __version__
    print("{} {}".format(__package__, __version__))
    sys.exit(0)

def start_consumer(config):
    """
    Start metrics consumer
    :param config:
    """
    reader = create_reader(config)
    writer = create_writer(config)
    encoder = load_encoder(config.encoder)
    client = Worker(reader, encoder, writer, config)
    client.consume()


def create_reader(config):
    try:
        return kafka_reader.KafkaReader(config.kafka_host,
                                        config.kafka_port,
                                        config.kafka_group,
                                        config.kafka_topic)
    except Exception as e:
        logging.error("The connection to Kafka can not be established: %s. Please check your config.", e)
        sys.exit(-1)


def create_writer(config):
    logging.info("Connecting to InfluxDB at %s:%s", config.influxdb_host, config.influxdb_port)
    try:
        return influxdb_writer.InfluxDBWriter(config.influxdb_host,
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
        logging.error("The connection to InfluxDB can not be established: %s", e)
        sys.exit(-2)


if __name__ == '__main__':
    main()
