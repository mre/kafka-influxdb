#!/usr/bin/env python
from profilehooks import profile
from kafka_influxdb.encoder import collectd_graphite_encoder


class ProfileCollectdGraphiteEncoder:

    def __init__(self, num_messages=10000):
        self.encoder = collectd_graphite_encoder.Encoder()
        self.sample_messages = b"""
            26f2fc918f50.load.load.shortterm 0.05 1436357630
            26f2fc918f50.load.load.midterm 0.05 1436357630
            26f2fc918f50.load.load.longterm 0.05 1436357630
            26f2fc918f50.cpu-0.cpu-user 30364 1436357630
            26f2fc918f50.memory.memory-buffered 743657472 1436357630
            myhost.load.load.shortterm 122.05 1436357630
            26f2fc918f50.load.load.shortterm 0.45 1436357630
            26f2fc918f50.load.load.midterm 0.04 1436357630
            26f2fc918f50.load.load.longterm 11.05 1436357630
            26f2fc918f50.cpu-0.cpu-user 30363292920 1436357630
            26f2fc918f50.memory.memory-buffered 743657472 1436357630
            """
        self.messages = b'\n'.join(num_messages * [self.sample_messages])

    @profile
    def profile_messages(self):
        self.encoder.encode(self.messages)


if __name__ == '__main__':
    profiler = ProfileCollectdGraphiteEncoder()
    profiler.profile_messages()
