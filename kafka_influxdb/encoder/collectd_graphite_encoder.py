import logging
from kafka_influxdb.encoder.escape_functions import influxdb_tag_escaper

try:
    # Test for mypy support (requires Python 3)
    from typing import Text
except:
    pass

class Encoder(object):
    """
    An encoder for the Collectd Graphite ASCII format
    See https://collectd.org/wiki/index.php/Graphite

    Sample measurements this encoder can handle:
    [prefix.]host.plugin.measurement[.postfix] value timestamp

    26f2fc918f50.load.load.shortterm 0.05 1436357630
    26f2fc918f50.load.load.midterm 0.05 1436357630
    26f2fc918f50.load.load.longterm 0.05 1436357630

    26f2fc918f50.cpu-0.cpu-user 30364 1436357630

    26f2fc918f50.memory.memory-buffered 743657472 1436357630

    The optional prefix and postifx can be set in the collectd plugin:
    <Plugin write_kafka>
        Property "metadata.broker.list" "kafka:9092"
        <Topic "metrics">
            Format Graphite
            GraphitePrefix "myprefix"
            GraphitePostfix "mypostfix"
        </Topic>
    </Plugin>
    """

    def __init__(self):
        self.escape_tag = influxdb_tag_escaper()

    def encode(self,
               msg,
               delimiter='.',
               prefix='',
               prefix_tag=None,
               postfix='',
               postfix_tag=None,
               ):
        # type: (bytes, Text, Text, Text, Text, Text) -> List[Text]
        """
        :param msg: Payload from reader
        :param delimiter: Delimiter between Graphite series parts
        :param prefix: Graphite prefix string
        :param prefix_tag: Tag to use for Graphite prefix
        :param postfix: Graphite postfix string
        :param postfix_tag: Tag to use for Graphite postfix
        :return: A list of encoded messages
        """
        # One message could consist of several measurements
        measurements = []

        for line in msg.decode().split("\n"):
            try:
                series, value, timestamp = line.split()
            except ValueError as e:
                logging.debug("Error in encoder: %s", e)
                continue
            # Strip prefix and postfix:
            series = series[len(prefix):len(series) - len(postfix)]
            # Split into tags
            hostname, measurement = series.split(delimiter, 1)
            measurement = measurement.replace(delimiter, '_')

            tags = {
                "host": hostname
            }
            if prefix_tag:
                if prefix.endswith(delimiter):
                    prefix = prefix[:-len(delimiter)]
                tags[prefix_tag] = prefix
            if postfix_tag:
                if postfix.endswith(delimiter):
                    postfix = postfix[:-len(delimiter)]
                tags[postfix_tag] = postfix

            encoded = ''.join([
                str(measurement),
                ',',
                ','.join('{}={}'.format(self.escape_tag(k), self.escape_tag(tags[k])) for k in tags),
                ' value=',
                str(value),
                ' ',
                timestamp
            ])
            measurements.append(encoded)
        return measurements
