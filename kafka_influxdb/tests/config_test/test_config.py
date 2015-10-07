import unittest
import os
from kafka_influxdb.config import loader

class Config:
    def __init__(self, configfile):
        self.configfile = configfile

class ParsedConfig:
    def __init__(self, kafka):
        self.kafka_host = kafka

class TestConfig(unittest.TestCase):
    def setUp(self):
        path = os.path.dirname(os.path.abspath(__file__))
        self.configfile = "{}/../fixtures/config.yaml".format(path)

    def test_load_config(self):
        parsed_config = loader.parse_configfile(self.configfile)
        self.assertEqual(parsed_config["kafka"]["host"], "kafkahost")
        self.assertEqual(parsed_config["kafka"]["port"], 1234)
        self.assertEqual(parsed_config["kafka"]["topic"], "kafkatopic")
        self.assertEqual(parsed_config["influxdb"]["host"], "influxdbhost")
        self.assertEqual(parsed_config["influxdb"]["port"], 9999)
        self.assertEqual(parsed_config["influxdb"]["user"], "hans")
        self.assertEqual(parsed_config["influxdb"]["password"], "hans")
        self.assertEqual(parsed_config["influxdb"]["dbname"], "influxdbname")
        self.assertEqual(parsed_config["influxdb"]["retention_policy"], "my_rp")
        self.assertEqual(parsed_config["encoder"], "collectd_graphite_encoder")
        self.assertEqual(parsed_config["benchmark"], False)
        self.assertEqual(parsed_config["buffer_size"], 444)
        self.assertEqual(parsed_config["statistics"], True)

    def test_override_config(self):
        default_config = {'kafka_host': 'defaulthost'}
        config = loader.overwrite_config(default_config, {'kafka_host': 'otherhost'})
        self.assertEqual(config['kafka_host'], 'otherhost')

if __name__ == '__main__':
    unittest.main()
