import sys
import logging
from kafka_influxdb.worker import Worker
from kafka_influxdb.writer import influxdb_writer
from kafka_influxdb.encoder import load_encoder
from kafka_influxdb.reader import load_reader
from kafka_influxdb.config import loader

__title__ = 'kafka_influxdb'
__author__ = 'Matthias Endler'
__license__ = 'Apache License 2.0'
__copyright__ = 'Copyright 2015, Matthias Endler under Apache License, v2.0'


def main():
    """
    Setup consumer
    """
    config = loader.load_config()
    if config.version:
        show_version()
    start_consumer(config)


def show_version():
    """
    Output current version and exit
    """
    from .version import __version__
    print("{} {}".format(__package__, __version__))
    sys.exit(0)


def start_consumer(config):
    """
    Start metrics consumer
    :param config:
    """
    logging.debug("Initializing Kafka Consumer")
    reader = load_reader(
        config.kafka_reader,
        config.kafka_host,
        config.kafka_port,
        config.kafka_group,
        config.kafka_topic
    )
    logging.debug("Initializing connection to InfluxDB at %s:%s",
                  config.influxdb_host, config.influxdb_port)
    writer = create_writer(config)
    logging.debug("Initializing message encoder: %s", config.encoder)
    encoder = load_encoder(config.encoder)
    client = Worker(reader, encoder, writer, config)
    client.consume()


def create_writer(config):
    """
    Create InfluxDB writer
    """
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


if __name__ == '__main__':
    main()
