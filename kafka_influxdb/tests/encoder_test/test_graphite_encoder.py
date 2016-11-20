import pytest

from kafka_influxdb.encoder import graphite_encoder
from kafka_influxdb.template import graphite


# TestGraphiteTemplate:
# metric-range is the number of dots '.' in the metric-name
@pytest.mark.parametrize("segments, result, templates", [
    (0, 'measurement', ['measurement', 'host.measurement', 'cpu.host.measurement']),
    (1, 'host.measurement', ['measurement', 'host.measurement', 'cpu.host.measurement']),
    (2, 'cpu.host.measurement', ['measurement', 'host.measurement', 'cpu.host.measurement']),
    (2, '.host.measurement', [
        'measurement', 'host.measurement', '.host.measurement']),
    # later templates override former templates of same range
    (2, 'cpu.host.measurement', [
        'measurement', 'host.measurement', '.host.measurement', 'cpu.host.measurement']),
    # return None if no template matches metric-range
    (2, None, [
        'measurement', 'host.measurement', 'dc.cpu.host.measurement']),
    # return wildcard template on non matching metric-range
    (3, 'host.measurement*', [
        'measurement', 'host.measurement*', 'dc.www.cpu.host.measurement']),
    # most specific wildcard should match first
    (3, 'dc.host.measurement*', [
        'measurement', 'host.measurement*',
        'dc.host.measurement*', 'dc.www.cpu.host.measurement']),
])
def test_get_template(segments, result, templates):
    # find matching template depending on metric-name segments
    # (number of '.' in metric-name)
    template = graphite.Template(templates)
    assert result == template.get(segments)


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
        (b'myhost 1.0 1436357630', ['myhost value=1.0 1436357630'], ['measurement']),
        (b'myhost.cpu 1.0 1436357630', ['myhost_cpu value=1.0 1436357630'], ['measurement*']),
        (b'myhost.cpu 1.0 1436357630', ['cpu,host=myhost value=1.0 1436357630'], ['host.measurement']),
        (b'myhost.cpu.load 1.0 1436357630', ['cpu_load,host=myhost value=1.0 1436357630'], ['host.measurement*']),
        (b'myhost.cpu.load 1.0 1436357630', ['load,host=myhost,cpu=cpu value=1.0 1436357630'], ['host.cpu.measurement']),
        (b'myhost.cpu.load 1.0 1436357630', ['load,host=myhost,cpu=cpu value=1.0 1436357630'], ['host.cpu.measurement*']),
        (b'myhost.cpu.load.shortterm 1.0 1436357630', ['load_shortterm,host=myhost,cpu=cpu value=1.0 1436357630'], ['host.cpu.measurement*']),
    ])
    def test_encode_template(self, message, key, templates):
        self.encoder = self.create_encoder(graphite.Template(templates))
        assert self.encoder.encode(message) == key
