import unittest
import os
import argparse
from mock import MagicMock
from kafka_influxdb.config import loader, default_config


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
        self.assertEqual(parsed_config["kafka"]["group"], "foogroup")
        self.assertEqual(parsed_config["influxdb"]["host"], "influxdbhost")
        self.assertEqual(parsed_config["influxdb"]["port"], 9999)
        self.assertEqual(parsed_config["influxdb"]["user"], "hans")
        self.assertEqual(parsed_config["influxdb"]["password"], "hans")
        self.assertEqual(parsed_config["influxdb"]["dbname"], "influxdbname")
        self.assertEqual(parsed_config["influxdb"]["use_ssl"], True)
        self.assertEqual(parsed_config["influxdb"]["verify_ssl"], True)
        self.assertEqual(parsed_config["influxdb"]["timeout"], 9000)
        self.assertEqual(parsed_config["influxdb"]["use_udp"], False)
        self.assertEqual(parsed_config["influxdb"]["retention_policy"], "my_rp")
        self.assertEqual(parsed_config["encoder"], "")
        self.assertEqual(parsed_config["buffer_size"], 444)
        self.assertEqual(parsed_config["statistics"], True)

    def test_argparse_flags(self):
        long_flags = [
            'influxdb_use_ssl',
            'influxdb_verify_ssl',
            'influxdb_use_udp',
            'statistics'
        ]
        for flag in long_flags:
            parsed = loader.parse_args(['--' + flag])
            self.assertEqual(parsed[flag], True)

        parsed = loader.parse_args(['-s'])
        self.assertEqual(parsed['statistics'], True)

    def test_cli_overwrite(self):
        # Fake commandline arguments
        # Argparse returns a namespace, not a dictionary
        fake_args = argparse.Namespace()
        fake_args.influxdb_use_ssl = False
        argparse.ArgumentParser.parse_args = MagicMock(return_value=fake_args)

        # Fake default config
        default_config.DEFAULT_CONFIG = MagicMock(return_value={'influxdb_use_ssl': True})
        config = loader.load_config()

        # Check if the default setting got overwritten
        self.assertEqual(config.influxdb_use_ssl, False)

    def test_overwrite_default_config(self):
        default_config = {'kafka_host': 'defaulthost'}
        config = loader.overwrite_config(default_config, {'kafka_host': 'otherhost'})
        self.assertEqual(config['kafka_host'], 'otherhost')


if __name__ == '__main__':
    unittest.main()
