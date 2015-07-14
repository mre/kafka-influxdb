import unittest
from kafka_influxdb.encoder import collectd_graphite_encoder

class TestCollectdGraphiteEncoder(unittest.TestCase):

    def setUp(self):
        self.encoder = collectd_graphite_encoder.Encoder()

    def test_encode_simple(self):
        msg = 'myhost.load.load.shortterm 0.05 1436357630'
        expected = 'load_load_shortterm,host=myhost value="0.05" 1436357630'
        self.assertEqual(self.encoder.encode(msg), expected)

    def test_encode_with_prefix(self):
        msg = 'mydatacenter.myhost.load.load.shortterm 0.45 1436357630'
        expected = 'load_load_shortterm,datacenter=mydatacenter,host=myhost value="0.45" 1436357630'
        self.assertEqual(self.encoder.encode(msg, prefix="mydatacenter.", prefix_tag="datacenter"), expected)
