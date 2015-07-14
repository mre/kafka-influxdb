import unittest
from mock import MagicMock
from kafka_influxdb.writer import influxdb_writer

class TestInfluxDBWriter(unittest.TestCase):

    def setUp(self):
        self.host = "myhost",
        self.port = 1234
        self.user = "test"
        self.password = "test"
        self.dbname = "mydb"
        self.writer = influxdb_writer.InfluxDBWriter(self.host, self.port, self.user, self.password, self.dbname)
        self.writer.client = MagicMock()

    def test_line_protocol_query(self):
        self.writer.write(["cpu,host=server01,region=uswest value=1.0 1434055562000"])
        self.writer.client.request.assert_called_once_with(url='write',
            expected_response_code=204,
            headers={'Content-type': 'application/octet-stream', 'Accept': 'text/plain'},
            params={'db': 'mydb'},
            data='cpu,host=server01,region=uswest value=1.0 1434055562000',
            method='POST')
