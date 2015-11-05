import unittest
from kafka_influxdb.encoder import echo_encoder


class TestEchoEncoder(unittest.TestCase):

    def setUp(self):
        self.encoder = echo_encoder.Encoder()
        self.messages = [
            "yeaal",
            ["this", "is", "a", "list"],
            {'hash': {'maps': 'rule'}},
            42,
            42.23
        ]

    def test_encode(self):
        for msg in self.messages:
            yield self.check_encode(msg)

    def check_encode(self, msg):
        """ Output must be same as input for echo sender """
        self.assertEqual(self.encoder.encode(msg), msg)
