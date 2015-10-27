import unittest
from kafka_influxdb.encoder import collectd_graphite_encoder


class TestCollectdGraphiteEncoder(unittest.TestCase):
    def setUp(self):
        self.encoder = collectd_graphite_encoder.Encoder()

    def test_encode_simple(self):
        msg = 'myhost.load.load.shortterm 0.05 1436357630'
        expected = ['load_load_shortterm,host=myhost value=0.05 1436357630']
        self.assertEqual(self.encoder.encode(msg), expected)

    def test_encode_with_prefix(self):
        msg = 'mydatacenter.myhost.load.load.shortterm 0.45 1436357630'
        expected = ['load_load_shortterm,datacenter=mydatacenter,host=myhost value=0.45 1436357630']
        self.assertEqual(self.encoder.encode(msg, prefix="mydatacenter.", prefix_tag="datacenter"), expected)

    def test_encode_multiple_values(self):
        msg = '26f2fc918f50.load.load.shortterm 0.05 1436357630\n' \
              '26f2fc918f50.load.load.midterm 0.06 1436357631\n' \
              '26f2fc918f50.load.load.longterm 0.07 1436357632'
        expected = [
            'load_load_shortterm,host=26f2fc918f50 value=0.05 1436357630',
            'load_load_midterm,host=26f2fc918f50 value=0.06 1436357631',
            'load_load_longterm,host=26f2fc918f50 value=0.07 1436357632',
        ]
        self.assertEqual(self.encoder.encode(msg), expected)

    def test_invalid_messages(self):
        invalid_messages = ['', '\n', 'bla', 'foo\nbar\nbaz']
        for msg in invalid_messages:
            self.assertEqual(self.encoder.encode(msg, prefix="mydatacenter.", prefix_tag="datacenter"), [])
