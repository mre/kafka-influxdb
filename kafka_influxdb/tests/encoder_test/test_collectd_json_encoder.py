import unittest
from kafka_influxdb.encoder import collectd_json_encoder
import re


class TestCollectdJsonEncoder(unittest.TestCase):
    def setUp(self):
        self.encoder = collectd_json_encoder.Encoder()

    def test_encode(self):
        """
        Test encoding of messages in collectd json format
        See https://github.com/mre/kafka-influxdb/issues/6
        :return:
        """
        msg = b"""
        [{"values":[0.6],"dstypes":["gauge"],"dsnames":["value"],"time":1444745144.824,"interval":10.000,"host":"xx.example.internal","plugin":"cpu","plugin_instance":"1","type":"percent","type_instance":"system"}]
            """

        encoded_messages = self.encoder.encode(msg)

        # We've encoded exactly one message
        self.assertEqual(len(encoded_messages), 1)

        encoded_message = encoded_messages[0]

        expected = '^cpu_1_percent,host=xx\.example\.internal,type_instance=system value=(\d\.\d+) 1444745144$'
        result = re.match(expected, encoded_message)

        # Due to floating point precision there might be a tiny difference between the expected and the actual value.
        self.assertIsNotNone(result, "Unexpected message format")
        self.assertEqual(len(result.groups()), 1)
        self.assertAlmostEqual(float(result.group(1)), 0.6)

    def test_multiple_measurements(self):
        """
        Test encoding of messages in collectd json format
        See https://github.com/mre/kafka-influxdb/issues/6
        :return:
        """
        msg = b"""
        [{"values":[0.6],"dstypes":["gauge"],"dsnames":["value"],"time":1444745144.824,"interval":10.000,"host":"xx.example.internal","plugin":"cpu","plugin_instance":"1","type":"percent","type_instance":"system"}]
        [{"values":[0.7],"dstypes":["gauge"],"dsnames":["value"],"time":1444745144.824,"interval":10.000,"host":"example.com","plugin":"cpu","plugin_instance":"1","type":"percent","type_instance":"user"}]
        [{"values":[37.7],"dstypes":["gauge"],"dsnames":["value"],"time":1444745144.824,"interval":10.000,"host":"myhost","plugin":"cpu","plugin_instance":"0","type":"percent","type_instance":"nice"}]
        [{"values":[0],"dstypes":["gauge"],"dsnames":["value"],"time":1444745145.824,"interval":10.000,"host":"myhost","plugin":"cpu","plugin_instance":"0","type":"percent","type_instance":"interrupt"}]
        [{"values":[1.1],"dstypes":["gauge"],"dsnames":["value"],"time":1444745136.182,"interval":10.000,"host":"myhost","plugin":"memory","plugin_instance":"","type":"percent","type_instance":"slab_recl"}]
            """
        expected = [
            ('cpu_1_percent,host=xx.example.internal,type_instance=system value=(.*) 1444745144', 0.6),
            ('cpu_1_percent,host=example.com,type_instance=user value=(.*) 1444745144', 0.7),
            ('cpu_0_percent,host=myhost,type_instance=nice value=(.*) 1444745144', 37.7),
            ('cpu_0_percent,host=myhost,type_instance=interrupt value=(.*) 1444745145', 0),
            ('memory_percent,host=myhost,type_instance=slab_recl value=(.*) 1444745136', 1.1)
        ]

        encoded_messages = self.encoder.encode(msg)

        # We've encoded exactly one message
        self.assertEqual(len(encoded_messages), 5)

        for encoded_message, expected in zip(encoded_messages, expected):
            expected_message, expected_value = expected
            result = re.match(expected_message, encoded_message)
            self.assertIsNotNone(result, "Unexpected message format")
            self.assertEqual(len(result.groups()), 1)
            self.assertAlmostEqual(float(result.group(1)), expected_value)

    def test_invalid_messages(self):
        invalid_messages = [b'', b'\n', b'bla', b'foo\nbar\nbaz']
        for msg in invalid_messages:
            self.assertEqual(self.encoder.encode(msg), [])

    def test_documentation_examples(self):
        msg = b"""
        [{"values":[0],"dstypes":["derive"],"dsnames":["value"],"time":1436372292.412,"interval":10.000,"host":"26f2fc918f50","plugin":"cpu","plugin_instance":"1","type":"cpu","type_instance":"interrupt"}]
            """
        expected = ['cpu_1_cpu,host=26f2fc918f50,type_instance=interrupt value=0 1436372292']
        self.assertEqual(self.encoder.encode(msg), expected)

    def test_multiple_fields(self):
        """
        Test supporting multiple fields in a sample
        [{"values":[0.2, 0.3],"dstypes":["derive"],"dsnames":["cpu_usage", "mem_usage"],"time":1436372292.412,"interval":10.000,"host":"26f2fc918f50","plugin":"sys_usage","plugin_instance":"1","type":"percent"}]
        """
        msg = b"""
        [{"values":[0.2, 0.3],"dstypes":["derive"],"dsnames":["cpu_usage", "mem_usage"],"time":1436372292.412,"interval":10.000,"host":"26f2fc918f50","plugin":"sys_usage","plugin_instance":"1","type":"percent"}]
        """

        encoded_messages = self.encoder.encode(msg)

        self.assertEqual(len(encoded_messages), 1)

        encoded_message = encoded_messages[0]

        expected = '^sys_usage_1_percent,host=26f2fc918f50 cpu_usage=(\d\.\d+),mem_usage=(\d\.\d+) 1436372292$'
        result = re.match(expected, encoded_message)

        # Due to floating point precision there might be a tiny difference between the expected and the actual value.
        self.assertIsNotNone(result, "Unexpected message format")
        self.assertEqual(len(result.groups()), 2)
        self.assertAlmostEqual(float(result.group(1)), 0.2)
        self.assertAlmostEqual(float(result.group(2)), 0.3)


"""
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


# See https://collectd.org/wiki/index.php/JSON

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

# See https://github.com/mjuenema/collectd-write_json

[
    {
        "dsnames": ['shorttem', 'midterm', 'longterm'],
        "dstypes": ['gauge', 'gauge', 'gauge'],
        "host": "localhost",
        "interval": 5.0,
        "plugin": "load",
        "plugin_instance": "",
        "time": 1432086959.8153536,
        "type": "load",
        "type_instance": "",
        "values": [
            0.0,
            0.01,
            0.050000000000000003
        ]
    }
]
"""
