# -*- coding: utf-8 -*-

import logging
import influxdb


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
        """ Initialize the given database """
        self.client.create_database(dbname)

    def write(self, msg, params=None, expected_response_code=204):
        """
        Write messages to InfluxDB database.
        Expects messages in line protocol format.
        See https://influxdb.com/docs/v0.9/write_protocols/line.html
        """
        if not params:
            # Use defaults
            params = self.params

        try:
            self.client.request(url='write',
                                method='POST',
                                params=params,
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
