import unittest
from kafka_influxdb.encoder import graphite_encoder
from kafka_influxdb.template import graphite
import pytest

class TestGraphiteEncoder(object):

    def setUp(self):
        self.encoder = self.create_encoder()

    @staticmethod
    def create_encoder(templates=None):
        return graphite_encoder.Encoder(templates)

    @pytest.mark.parametrize("message, key", [
        (b'\n\nbla\nfoo\nbar\nbaz', []),
        (b'myhost.load.load.shortterm 0.05 1436357630', ['myhost_load_load_shortterm value=0.05 1436357630']),
        (b'myhost.load.shortterm 0.05 1436357630', ['myhost_load_shortterm value=0.05 1436357630']),
        (b'myhost.load.shortterm "hello" 1436357630', ['myhost_load_shortterm value="hello" 1436357630']),
        (b'myhost.load1 0.05 1436357630\nmyhost.load2 0.05 1436357630', ['myhost_load1 value=0.05 1436357630', 'myhost_load2 value=0.05 1436357630']),
    ])
    def test_encode_simple(self, message, key):
        self.encoder = self.create_encoder(graphite.Template([]))
        assert self.encoder.encode(message) == key

    @pytest.mark.parametrize("message, key, templates", [
        # Valid, even though no template matches (fall back to default matching full key)
        (b'myhost 1.0 1436357630', ['myhost value=1.0 1436357630'], ['*']),
        (b'myhost 1.0 1436357630', ['myhost value=1.0 1436357630'], ['host']),
        #(b'myhost.cpu 1.0 1436357630', ['cpu,host=myhost value=1.0 1436357630'], ['host.*']),
        #(b'myhost.cpu.load 1.0 1436357630', ['cpu_load,host=myhost value=1.0 1436357630'], ['host.*']),
        #(b'myhost.cpu.load 1.0 1436357630', ['load,cpu=cpu,host=myhost value=1.0 1436357630'], ['host.cpu.*']),
    ])
    def test_encode_template(self, message, key, templates):
        self.encoder = self.create_encoder(graphite.Template(templates))
        assert self.encoder.encode(message) == key
