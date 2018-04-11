#!/usr/bin/env python
from profilehooks import profile
from kafka_influxdb.encoder import collectd_json_encoder


class ProfileCollectdJsonEncoder:

    def __init__(self, num_messages=10000):
        self.encoder = collectd_json_encoder.Encoder()
        self.sample_messages = b"""
            [{"values":[0.6],"dstypes":["gauge"],"dsnames":["value"],"time":1444745144.824,"interval":10.000,"host":"xx.example.internal","plugin":"cpu","plugin_instance":"1","type":"percent","type_instance":"system"}]
            [{"values":[0.7],"dstypes":["gauge"],"dsnames":["value"],"time":1444745144.824,"interval":10.000,"host":"example.com","plugin":"cpu","plugin_instance":"1","type":"percent","type_instance":"user"}]
            [{"values":[37.7],"dstypes":["gauge"],"dsnames":["value"],"time":1444745144.824,"interval":10.000,"host":"myhost","plugin":"cpu","plugin_instance":"0","type":"percent","type_instance":"nice"}]
            [{"values":[0],"dstypes":["gauge"],"dsnames":["value"],"time":1444745145.824,"interval":10.000,"host":"myhost","plugin":"cpu","plugin_instance":"0","type":"percent","type_instance":"interrupt"}]
            [{"values":[1.1],"dstypes":["gauge"],"dsnames":["value"],"time":1444745136.182,"interval":10.000,"host":"myhost","plugin":"memory","plugin_instance":"","type":"percent","type_instance":"slab_recl"}]
            """
        self.messages = b'\n'.join(num_messages * [self.sample_messages])

    @profile
    def profile_messages(self):
        self.encoder.encode(self.messages)


if __name__ == '__main__':
    profiler = ProfileCollectdJsonEncoder()
    profiler.profile_messages()
