import unittest

from encoder import echo_encoder

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
            yield check_encode(msg)

    def check_encode(msg):
        """ Output must be same as input for echo sender """
        self.assertEqual(self.encoder.encode(msg), msg)

if __name__ == '__main__':
    unittest.main()
