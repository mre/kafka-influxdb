import logging
#from kafka_influxdb.encoder.escape_functions import influxdb_tag_escaper

try:
    # Test for mypy support (requires Python 3)
    from typing import Text
except ImportError:
    pass

class Encoder(object):
    """
    An encoder for the Graphite ASCII format
    See https://collectd.org/wiki/index.php/Graphite

    Sample measurements this encoder can handle:

    26f2fc918f50.load.load.shortterm 0.05 1436357630
    webserver.cpu-0.cpu-user 30364 1436357630
    datacenter.webserver.memory.memory-buffered 743657472 1436357630
    """

    def __init__(self, templates=None):
        self.templates = templates or {}
        #self.escape_tag = influxdb_tag_escaper()

    def encode(self, messages):
        """
        :param messages: Payload from reader as Bytes. Can hold multiple
                         messages
        :return: A list of encoded messages
        """
        measurements = []
        for line in messages.decode().split("\n"):
            try:
                name, value, timestamp = line.split()
            except ValueError as e:
                logging.debug("Error in encoder: %s", e)
                continue
            segments = len(name.split('.'))
            template = self.templates.get(segments)
            key = self.create_key(name, template)
            influx_entry = self.create_entry(key, value, timestamp)
            measurements.append(influx_entry)
        return measurements

    @staticmethod
    def create_key(name, template):
        if not template:
            return name.replace('.', '_')
        return name

    @staticmethod
    def create_entry(key, value, timestamp):
        return '{} value={} {}'.format(key, value, timestamp)
