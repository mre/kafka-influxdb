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
                measurement = [entry['plugin']]
                # Check if plugin_instance is set and not empty
                if 'plugin_instance' in entry and entry['plugin_instance']:
                    measurement.append('-')
                    measurement.append(entry['plugin_instance'])
                # Todo: Read all values from collect json message
                value = str(entry['values'][0])
                # Always use millisecond precision for the timestamp
                timestamp = "{:.3f}".format(entry['time'])
                measurement.extend([
                    '_',
                    entry['plugin'],
                    '-',
                    entry['type_instance'],
                    ',',
                    'host=',
                    entry['host'],
                    ' ',
                    'value',
                    '=',
                    value,
                    ' ',
                    timestamp
                ])
                measurements.append(''.join(measurement))
        return measurements

    @staticmethod
    def parse_line(line):
        return json.loads(line, {'precise_float': True})
