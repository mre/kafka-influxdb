# PyPy does not have ultrajson
# See https://github.com/esnme/ultrajson/issues/98
try:
    import ujson as json
except ImportError:
    import json

import logging

try:
    # Test for mypy support (requires Python 3)
    from typing import List, Text
except:
    pass


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
    
    The following measurement format is also supported, which has more than one value for each sample.
    [{"values":[0.2, 0.3],"dstypes":["derive"],"dsnames":["cpu_usage", "mem_usage"],"time":1436372292.412,"interval":10.000,"host":"26f2fc918f50","plugin":"cpu","plugin_instance":"1","type":"cpu","type_instance":"interrupt"}]
    """

    def encode(self, msg):
        # type: (bytes) -> List[Text]
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
                try:
                    # to set plugin, plugin_instance as the measurement name, just need pass ['plugin', 'plugin_instance']
                    measurement = Encoder.format_measurement_name(entry, ['plugin', 'plugin_instance', 'type'])
                    tags = Encoder.format_tags(entry, ['host', 'type_instance'])
                    value = Encoder.format_value(entry)
                    time = Encoder.format_time(entry)
                    measurements.append(Encoder.compose_data(measurement, tags, value, time))
                except Exception as e:
                    logging.debug("Error in input data: %s. Skipping.", e)
                    continue
        return measurements

    @staticmethod
    def parse_line(line):
        # return json.loads(line, {'precise_float': True})
        # for influxdb version > 0.9, timestamp is an integer
        return json.loads(line)

    # following methods are added to support customizing measurement name, tags much more flexible
    @staticmethod
    def compose_data(measurement, tags, value, time):
        data = "%s,%s %s %s" % (measurement, tags, value, time)
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
            return "value=%s" % entry['values'][0]
        else:
            # influxdb supports writing a record with multiple field values.
            # e.g: 'cpu_load_short,host=server01,region=us-west mem=0.1,cpu=0.2 1422568543702900257'
            field_pairs = []
            for key, value in zip(entry['dsnames'], values):
                field_pairs.append("%s=%s" % (key, value))
            return ','.join(field_pairs)
