from . import default_config
import yaml
import logging
import argparse
import collections
import sys


class ObjectView(object):
    def __init__(self, d):
        self.__dict__ = d


def load_config():
    """
    Load settings from default config and optionally
    overwrite with config file and commandline parameters
    (in that order).

    Note: Commandline parameters are of the form
    --kafka_host="localhost"
    to make them easy to enter from the cli
    while the config file parameters are stored in a dict
    {kafka: { host: localhost }}
    to avoid redundancy in the key name.
    So to merge them, we flatten all keys.
    """
    # We start with the default config
    config = flatten(default_config.DEFAULT_CONFIG)

    # Read commandline arguments
    cli_config = flatten(parse_args())

    if "configfile" in cli_config:
        print("Reading config file {}".format(cli_config['configfile']))
        configfile = flatten(parse_configfile(cli_config['configfile']))
        config = overwrite_config(config, configfile)

    # Parameters from commandline take precedence over all others
    config = overwrite_config(config, cli_config)

    # Set verbosity level
    if 'verbose' in config:
        if config['verbose'] == 1:
            logging.getLogger().setLevel(logging.INFO)
        elif config['verbose'] > 1:
            logging.getLogger().setLevel(logging.DEBUG)

    return ObjectView(config)


def overwrite_config(old_values, new_values):
    config = old_values.copy()
    config.update(new_values)
    return config


def parse_configfile(configfile):
    """
    Read settings from file
    """
    with open(configfile) as f:
        try:
            return yaml.safe_load(f)
        except Exception as e:
            logging.fatal("Could not load default config file: ", e)
            exit(-1)


def flatten(d, parent_key='', sep='_'):
    """
    Flatten keys in a dictionary
    Example:
    flatten({'a': 1, 'c': {'a': 2, 'b': {'x': 5, 'y' : 10}}, 'd': [1, 2, 3]})
    => {'a': 1, 'c_a': 2, 'c_b_x': 5, 'd': [1, 2, 3], 'c_b_y': 10}
    """
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def parse_args(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(description='A Kafka consumer for InfluxDB',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--kafka_host', type=str, default=argparse.SUPPRESS,
                        help="Hostname or IP of Kafka message broker (default: localhost)")
    parser.add_argument('--kafka_port', type=int, default=argparse.SUPPRESS,
                        help="Port of Kafka message broker (default: 9092)")
    parser.add_argument('--kafka_topic', type=str, default=argparse.SUPPRESS,
                        help="Topic for metrics (default: my_topic)")
    parser.add_argument('--kafka_group', type=str, default=argparse.SUPPRESS,
                        help="Kafka consumer group (default: my_group)")
    parser.add_argument('--influxdb_host', type=str, default=argparse.SUPPRESS,
                        help="InfluxDB hostname or IP (default: localhost)")
    parser.add_argument('--influxdb_port', type=int, default=argparse.SUPPRESS,
                        help="InfluxDB API port (default: 8086)")
    parser.add_argument('--influxdb_user', type=str, default=argparse.SUPPRESS,
                        help="InfluxDB username (default: root)")
    parser.add_argument('--influxdb_password', type=str, default=argparse.SUPPRESS,
                        help="InfluxDB password (default: root)")
    parser.add_argument('--influxdb_dbname', type=str, default=argparse.SUPPRESS,
                        help="InfluxDB database to write metrics into (default: metrics)")
    parser.add_argument('--influxdb_use_ssl', default=argparse.SUPPRESS, action="store_true",
                        help="Use SSL connection for InfluxDB (default: False)")
    parser.add_argument('--influxdb_verify_ssl', default=argparse.SUPPRESS, action="store_true",
                        help="Verify the SSL certificate before connecting (default: False)")
    parser.add_argument('--influxdb_timeout', type=int, default=argparse.SUPPRESS,
                        help="Max number of seconds to establish a connection to InfluxDB (default: 5)")
    parser.add_argument('--influxdb_use_udp', default=argparse.SUPPRESS, action="store_true",
                        help="Use UDP connection for InfluxDB (default: False)")
    parser.add_argument('--influxdb_retention_policy', type=str, default=argparse.SUPPRESS,
                        help="Retention policy for incoming metrics (default: default)")
    parser.add_argument('--influxdb_time_precision', type=str, default=argparse.SUPPRESS,
                        help="Precision of incoming metrics. Can be one of 's', 'm', 'ms', 'u' (default: s)")
    parser.add_argument('--encoder', type=str, default=argparse.SUPPRESS,
                        help="Input encoder which converts an incoming message to dictionary "
                             "(default: collectd_graphite_encoder)")
    parser.add_argument('--buffer_size', type=int, default=argparse.SUPPRESS,
                        help="Maximum number of messages that will be collected before flushing to the backend "
                             "(default: 1000)")
    parser.add_argument('-c', '--configfile', type=str, default=argparse.SUPPRESS,
                        help="Configfile path (default: None)")
    parser.add_argument('-s', '--statistics', default=argparse.SUPPRESS, action="store_true",
                        help="Show performance statistics (default: True)")
    parser.add_argument('-b', '--benchmark', default=argparse.SUPPRESS, action="store_true",
                        help="Run benchmark (default: False)")
    parser.add_argument('-v', '--verbose', action='count', default=argparse.SUPPRESS,
                        help="Set verbosity level. Increase verbosity by adding a v: -v -vv -vvv (default: 0)")
    parser.add_argument('--version', action="store_true", help="Show version")
    cli_args = parser.parse_args(args)
    # Convert config from argparse Namespace to dict
    return vars(cli_args)
