class Encoder(object):
    """
    An encoder for the Collectd Graphite ASCII format
    See https://collectd.org/wiki/index.php/Graphite

    Sample measurements:
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
            msg, # Payload from reader
            delimiter='.', # Delimiter between Graphite series parts
            prefix='', # Graphite prefix string
            prefix_tag=None, # Tag to use for Graphite prefix
            postfix='', # Graphite postfix string
            postfix_tag=None, # Tag to use for Graphite postfix
            **kwargs):
        # One message could consist of several measurements
        for line in msg.split("\n"):
            series, value, timestamp = line.split()
            # Strip prefix and postfix:
            series = series[len(prefix):len(series)-len(postfix)]
            # Split into tags
            hostname, measurement = series.split(delimiter, 1)
            measurement = measurement.replace(delimiter, '_')

            tags = {
                "host": hostname
            }
            if prefix_tag:
                if prefix.endswith(delimiter):
                    prefix= prefix[:-len(delimiter)]
                tags[prefix_tag] = prefix
            if postfix_tag:
                if postfix.endswith(delimiter):
                    postfix = postfix [:-len(delimiter)]
                tags[postfix_tag] = postfix

            return self.escape(measurement) + "," + ','.join("{}={}".format(self.escape(k),self.escape(tags[k])) for k in sorted(tags)) + " value=" + value + " " + timestamp

    def escape(self, str):
        return str.replace(" ", "\ ").replace(",", "\, ")
