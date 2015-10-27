import unittest
from mock import MagicMock
from kafka_influxdb.writer import influxdb_writer
import influxdb


class TestInfluxDBWriter(unittest.TestCase):
    def setUp(self):
        self.host = "myhost",
        self.port = 1234
        self.user = "test"
        self.password = "test"
        self.dbname = "mydb"
        self.verify_ssl = False

    def create_writer(self, use_ssl=False, use_udp=False, timeout=None):
        self.use_ssl = use_ssl
        self.use_udp = use_udp
        self.timeout = timeout
        return influxdb_writer.InfluxDBWriter(self.host,
                                              self.port,
                                              self.user,
                                              self.password,
                                              self.dbname,
                                              self.use_ssl,
                                              self.verify_ssl,
                                              self.timeout,
                                              self.use_udp,
                                              self.port)

    def test_write(self):
        writer = self.create_writer()
        writer.client = MagicMock()
        writer.write([
            "cpu,host=server01,region=uswest value=1.0 1434055562000",
            "cpu,host=server02,region=uswest value=2.0 1434055562005"
        ])
        writer.client.request.assert_called_once_with(url='write',
                                                      expected_response_code=204,
                                                      headers={'Content-type': 'application/octet-stream',
                                                               'Accept': 'text/plain'},
                                                      params={'rp': 1234, 'db': 'mydb'},
                                                      data='cpu,host=server01,region=uswest value=1.0 1434055562000\n'
                                                      'cpu,host=server02,region=uswest value=2.0 1434055562005',
                                                      method='POST')

    def test_ssl_connection(self):
        influxdb.InfluxDBClient = MagicMock()
        writer = self.create_writer(True)
        writer.client = MagicMock()
        influxdb.InfluxDBClient.assert_called_once_with(
            self.host, self.port, self.user, self.password, self.dbname,
            self.use_ssl, self.verify_ssl, self.timeout, self.use_udp, self.port
        )
