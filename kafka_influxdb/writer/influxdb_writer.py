# -*- coding: utf-8 -*-

import logging
import influxdb

try:
    # Test for mypy support (requires Python 3)
    from typing import Mapping, Text
except:
    pass


class InfluxDBWriter(object):
    DEFAULT_HEADERS = {
        'Content-type': 'application/octet-stream',
        'Accept': 'text/plain'
    }

    def __init__(self,
                 host,
                 port,
                 user,
                 password,
                 dbname,
                 use_ssl=False,
                 verify_ssl=False,
                 timeout=5,
                 use_udp=False,
                 retention_policy=None,
                 time_precision=None):
        """
        Initialize InfluxDB writer
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.dbname = dbname
        self.use_ssl = use_ssl
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        self.use_udp = use_udp
        self.retention_policy = retention_policy
        self.time_precision = time_precision

        self.params = {'db': self.dbname}
        self.headers = self.DEFAULT_HEADERS
        if time_precision:
            self.params['precision'] = time_precision
        if retention_policy:
            self.params['rp'] = retention_policy

        logging.info("Connecting to InfluxDB at %s:%s (SSL: %r, UDP: %r)", host, port, use_ssl, use_udp)
        self.client = self.create_client()
        logging.info("Creating database %s if not exists", dbname)

    def create_client(self):
        """
        Create an InfluxDB client
        """
        return influxdb.InfluxDBClient(self.host,
                                       self.port,
                                       self.user,
                                       self.password,
                                       self.dbname,
                                       self.use_ssl,
                                       self.verify_ssl,
                                       self.timeout,
                                       self.use_udp,
                                       self.port)

    def create_database(self, dbname):
        # type: (Text) -> bool
        """
        Initialize the given database
        :param dbname:
        """
        self.client.create_database(dbname)

    def write(self, msg, params=None, expected_response_code=204):
        # type: (Text, Mapping[str, str], int) -> bool
        """
        Write messages to InfluxDB database.
        Expects messages in line protocol format.
        See https://influxdb.com/docs/v0.9/write_protocols/line.html
        :param expected_response_code:
        :param params:
        :param msg:
        """
        if not params:
            # Use defaults
            params = self.params

        try:
            self.client.request(url='write',
                                method='POST',
                                params=params,
                                data="\n".join(msg),
                                expected_response_code=expected_response_code,
                                headers=self.headers
                                )
        except Exception as e:
            logging.warning("Cannot write data points: %s", e)
            return False
        return True
