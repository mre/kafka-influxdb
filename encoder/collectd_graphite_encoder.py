class Encoder():
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
    26f2fc918f50.memory.memory-cached 3612651520 1436357630

    The optional prefix and postifx can be set in the collectd plugin:
    <Plugin write_graphite>
      <Node "influxdb">
        Host "127.0.0.1"
        Port "2003"
        Protocol "tcp"
        LogSendErrors true
        Prefix "prefix."
        Postfix ""
        StoreRates true
        AlwaysAppendDS false
        EscapeCharacter "."
      </Node>
    </Plugin>
    """
    def encode(self, msg, delimiter='.', prefix='', prefix_tag=None, postfix='', postfix_tag=None, **kwargs):
        """
        InfluxDB v0.9 data format:
        data = [
            {
                "measurement": "cpu_load_short",
                "tags": {
                    "host": "server01",
                    "region": "us-west"
                },
                "time": "2009-11-10T23:00:00Z",
                "fields": {
                    "value": 0.64
                }
            }
        ]
        """
        series, value, timestamp = msg.split()
        # Strip prefix and postfix:
        series = series[len(prefix):len(series)-len(postfix)]
        # Split into tags
        hostname, measurement = series.split(delimiter, 1)
        measurement = measurement.replace(delimiter, '_')

        tags = {}
        tags["host"] = hostname
        if prefix_tag:
            if prefix.endswith(delimiter):
                prefix= prefix[:-len(delimiter)]
            tags[prefix_tag] = prefix
        if postfix_tag:
            if postfix.endswith(delimiter):
                postfix = postfix [:-len(delimiter)]
            tags[postfix_tag] = postfix

        return {
            "measurement": measurement,
            "tags": tags,
            "time": timestamp + "s", # Time in seconds
            "fields": {
                "value": value
            }
        }
