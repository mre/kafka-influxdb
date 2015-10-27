from six import binary_type, text_type
import logging

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

    def encode(self,
               msg,  # Payload from reader
               delimiter='.',  # Delimiter between Graphite series parts
               prefix='',  # Graphite prefix string
               prefix_tag=None,  # Tag to use for Graphite prefix
               postfix='',  # Graphite postfix string
               postfix_tag=None,  # Tag to use for Graphite postfix
               ):
        # One message could consist of several measurements
        measurements = []

        for line in msg.split("\n"):
            try:
                series, value, timestamp = line.split()
            except ValueError, e:
                logging.debug("Error in encoder: %s", e.message)
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

            encoded = self.escape_measurement(measurement) + ',' \
                + ','.join('{}={}'.format(self.escape_tag(k), self.escape_tag(tags[k])) for k in sorted(tags)) \
                + ' value=' + self.escape_value(value) + ' ' + timestamp
            measurements.append(encoded)
        return measurements

    @staticmethod
    def escape_tag(tag):
        return tag.replace(
            "\\", "\\\\"
        ).replace(
            " ", "\\ "
        ).replace(
            ",", "\\,"
        ).replace(
            "=", "\\="
        )

    def escape_value(self, value):
        value = self.escape_measurement(value)
        return str(value)

    @staticmethod
    def escape_measurement(data):
        """
        Try to return a text aka unicode object from the given data.
        """
        if isinstance(data, binary_type):
            return unicode(data, 'utf-8')
        else:
            return data
