import unittest
from kafka_influxdb.encoder import collectd_graphite_encoder


class TestCollectdGraphiteEncoder(unittest.TestCase):
    def setUp(self):
        self.encoder = collectd_graphite_encoder.Encoder()

    def test_encode_simple(self):
        msg = b'myhost.load.load.shortterm 0.05 1436357630'
        expected = ['load_load_shortterm,host=myhost value=0.05 1436357630']
        self.assertEqual(self.encoder.encode(msg), expected)

    def test_encode_with_prefix(self):
        msg = b'mydatacenter.myhost.load.load.shortterm 0.45 1436357630'

        # The official documentation states that tags should be sorted for performance reasons.
        # As of now they will be sorted on the InfluxDB side anyway (which is probably faster).
        # (See https://influxdb.com/docs/v0.9/write_protocols/line.html#key for more info)
        # So we don't sort the tags to make the encoder faster.
        # As a consequence they can appear in any order. Test for all combinations.
        expected1 = ['load_load_shortterm,datacenter=mydatacenter,host=myhost value=0.45 1436357630']
        expected2 = ['load_load_shortterm,host=myhost,datacenter=mydatacenter value=0.45 1436357630']

        if self.encoder.encode(msg, prefix="mydatacenter.", prefix_tag="datacenter") == expected1:
            return
        if self.encoder.encode(msg, prefix="mydatacenter.", prefix_tag="datacenter") == expected2:
            return
        raise self.failureException()

    def test_encode_multiple_values(self):
        msg = b'26f2fc918f50.load.load.shortterm 0.05 1436357630\n' \
              b'26f2fc918f50.load.load.midterm 0.06 1436357631\n' \
              b'26f2fc918f50.load.load.longterm 0.07 1436357632'
        expected = [
            'load_load_shortterm,host=26f2fc918f50 value=0.05 1436357630',
            'load_load_midterm,host=26f2fc918f50 value=0.06 1436357631',
            'load_load_longterm,host=26f2fc918f50 value=0.07 1436357632',
        ]
        self.assertEqual(self.encoder.encode(msg), expected)

    def test_invalid_messages(self):
        invalid_messages = [b'', b'\n', b'bla', b'foo\nbar\nbaz']
        for msg in invalid_messages:
            self.assertEqual(self.encoder.encode(msg, prefix="mydatacenter.", prefix_tag="datacenter"), [])
