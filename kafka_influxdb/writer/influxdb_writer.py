# -*- coding: utf-8 -*-

import logging
import influxdb
import sys
import requests

class InfluxDBWriter(object):

    def __init__(self, host, port, user, password, dbname, retention_policy=None, time_precision=None):
        """
        Initialize InfluxDB writer
        """
        self.retention_policy = retention_policy
        self.time_precision = time_precision
        self.dbname = dbname
        self.headers = {
            'Content-type': 'application/octet-stream',
            'Accept': 'text/plain'
        }
        self.params = { 'db': self.dbname}
        if time_precision is not None:
            self.params['precision'] = time_precision
        if retention_policy is not None:
            self.params['rp'] = retention_policy
        logging.info("Connecting to InfluxDB at %s:%s...", host, port)
        self.client = influxdb.InfluxDBClient(host, port, user, password, dbname)
        logging.info("Creating database %s if not exists", dbname)

    def create_database(self, dbname):
        """ Initialize the given database """
        self.client.create_database(dbname)


    def write(self, msg, params=None, expected_response_code=204):
        """
        Write messages to InfluxDB database.
        Expects messages in line protocol format.
        See https://influxdb.com/docs/v0.9/write_protocols/line.html
        """
        try:
            self.client.request(url='write',
                                method='POST',
                                params=self.params,
                                data="\n".join(m.encode('utf-8') for m in msg),
                                expected_response_code=expected_response_code,
                                headers=self.headers
                                )
        except Exception as e:
            logging.warning("Cannot write data points: %s", e)
            return False
        return True

    def write08(self):
        """
        TODO: Write in InfluxDB legacy 08 format:
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
        raise NotImplementedError
