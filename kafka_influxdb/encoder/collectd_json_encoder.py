# PyPy does not have ultrajson
# See https://github.com/esnme/ultrajson/issues/98
try:
    import ujson as json
except ImportError:
    import json

import logging


class Encoder(object):
    """
    An encoder for the Collectd JSON format
    See https://collectd.org/wiki/index.php/JSON

    Sample measurements:

    [{"values":[0],"dstypes":["derive"],"dsnames":["value"],"time":1436372292.412,"interval":10.000,"host":"26f2fc918f50","plugin":"cpu","plugin_instance":"1","type":"cpu","type_instance":"interrupt"}]

    [
       {
         "values":  [1901474177],
         "dstypes":  ["counter"],
         "dsnames":    ["value"],
         "time":      1280959128,
         "interval":          10,
         "host":            "leeloo.octo.it",
         "plugin":          "cpu",
         "plugin_instance": "0",
         "type":            "cpu",
         "type_instance":   "idle"
       }
    ]
    """
    def encode(self, msg):
        measurements = []

        for line in msg.decode().split("\n"):
            try:
                # Set flag for float precision to get the same
                # results for Python 2 and 3.
                json_object = self.parse_line(line)
            except ValueError as e:
                logging.debug("Error in encoder: %s", e)
                continue
            for entry in json_object:
                # people can customize the measurement name, tags much more flexible
                # to set plugin, plugin_instance as the measurement name, just need to pass ['plugin', 'plugin_instance']
                measurement = Encoder.format_measurement_name(entry, ['plugin', 'plugin_instance', 'type'])
                tags = Encoder.format_tags(entry, ['host', 'type_instance'])
                value = Encoder.format_value(entry)
                time = Encoder.format_time(entry)
                measurements.append(Encoder.compose_data(measurement, tags, value, time))
        return measurements

    @staticmethod
    def parse_line(line):
        # return json.loads(line, {'precise_float': True})
        # for influxdb version > 0.9, timestamp is an integer
        return json.loads(line)

    # following methods are added to support customizing measurement name, tags much more flexible
    @staticmethod
    def compose_data(measurement, tags, value, time):
        data = "%s,%s value=%s %s" % (measurement, tags, value, time)
        return data

    @staticmethod
    def format_measurement_name(entry, args):
        name = []
        for arg in args:
            if arg in entry:
                # avoid to add extra _ if some entry value is None
                if entry[arg] != '':
                    name.append(entry[arg])
        return '_'.join(name)

    @staticmethod
    def format_tags(entry, args):
        tag = []
        for arg in args:
            if arg in entry:
                # to avoid add None as tag value
                if entry[arg] != '':
                    tag.append("%s=%s" % (arg, entry[arg]))
        return ','.join(tag)

    @staticmethod
    def format_time(entry):
        return int(float(entry['time']))

    @staticmethod
    def format_value(entry):
        values = entry['values']
        if len(values) == 1:
            return entry['values'][0]
        else:
            # support to add multiple values
            value = ' '.join(str(value) for value in values)
            return '"%s"' % value


