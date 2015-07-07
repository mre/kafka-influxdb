# -*- coding: utf-8 -*-

import logging
import influxdb

class InfluxDBWriter(object):

	def __init__(self, host, port, user, password, dbname, retention_policy):
		""" Initialize InfluxDB writer """
		logging.info("Connecting to InfluxDB at %s:%s...", host, port)
		self.retention_policy = retention_policy
		influxdb_client = influxdb.InfluxDBClient(host, port, user, password, dbname)

	def write(self, msg):
		""" Write messages to InfluxDB database"""
		if self.version_0_9:
			data = self.metrics.points
		else:
			data = [self.metrics.__dict__]
		self.client.write_points(data, "s", self.config.influxdb_dbname, self.retention_policy)

"""
InfluxDB 09:
>>> data = [
    {
        "measurement": "cpu_load_short",
        "tags": {
            "host": "server01",
            "region": "us-west"
        },
        "time": "2009-11-10T23:00:00Z",
        "fields": {
            "value": 0.64
        }
    }
]

>>> client = InfluxDBClient('localhost', 8086, 'root', 'root', 'example')

>>> client.create_database('example')

>>> client.write_points(data)
client.write_points(data,
                     time_precision=None,
                     database=None,
                     retention_policy=None,
                     tags=None,
                     batch_size=None,
                     ):

---------

InfluxDB legacy 08:
 data = [
            {
                "name": "cpu_load_short",
                "columns": [
                    "value"
                ]
                "points": [
                    [
                        12
                    ]
                ],
            }
        ]

        client.write_points(data, time_precision='s', *args, **kwargs):

"""
