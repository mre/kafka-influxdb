from kafka.client import KafkaClient
from kafka.consumer import SimpleConsumer
from influxdb import InfluxDBClient # TODO import dynamically. If version 0.9 we have different requirements!
import json
import argparse
import time
import yaml
from collections import defaultdict
from clients.influxdbdata09 import InfluxDBData09
from clients.influxdbdata import InfluxDBData
from clients.kafkalistener import KafkaListener

DB_VERSION_DEFAULT = 0.8
DB_VERSION_APICHANGE = 0.9


def main(config):
	if config.configfile is not None and config.configfile != u'':
		read_config_file(config)
		if config.verbose:
			log("Config read: %s" % config)

	kafka = KafkaClient("{0}:{1}".format(config.kafka_host, config.kafka_port))

	client = InfluxDBClient(config.influxdb_host,
				config.influxdb_port,
				config.influxdb_user,
				config.influxdb_password,
				config.influxdb_dbname)

	listener = KafkaListener(kafka, client, config)
	
	try:	
		listener.listen()
	except KeyboardInterrupt:
		error_log("Shutdown.")
		listener.abort()

def read_config_file(config):
	values = None
	try:
		f = open(config.configfile)
		values = yaml.safe_load(f)
		f.close()
		set_config_values(config, values)

	except Exception as inst:
		error_log("Could not open config file %s : %s" % (config.configfile, inst), True)

def set_config_values(config, values, prefix = ''):
	for key, value in values.iteritems() :
		if type(value) == type(dict()):
			set_config_values(config, value, "%s_" % key)
		elif value != u'':
			setattr(config, "%s%s" % (prefix, key), value)
			
		
def log(msg):
	print msg # maybe redirect to logfile
	
def error_log(msg, die=False):
	print msg # TODO
	if die:
		exit()

def get_millis():
	return int(round(time.time() * 1000))



def parse_args():
	parser = argparse.ArgumentParser(description='A Kafka consumer for InfluxDB',
					formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('--kafka_host', type=str, default='localhost', required=False)
	parser.add_argument('--kafka_port', type=int, default=9092, required=False)
	parser.add_argument('--kafka_topic', type=str, default='test', required=False)
	parser.add_argument('--kafka_group', type=str, default='my_group', required=False)
	parser.add_argument('--influxdb_host', type=str, default='localhost', required=False)
	parser.add_argument('--influxdb_port', type=int, default=8086, required=False)
	parser.add_argument('--influxdb_user', type=str, default='root', required=False)
	parser.add_argument('--influxdb_password', type=str, default='root', required=False)
	parser.add_argument('--influxdb_dbname', type=str, default='kafka', required=False)
	parser.add_argument('--influxdb_data_name', type=str, default='statsd', required=False)
	parser.add_argument('--influxdb_columns', type=str, default=['counter'], required=False)
	parser.add_argument('--influxdb_version', type=str, default=DB_VERSION_DEFAULT, required=False)
	parser.add_argument('--buffer_size', type=int, default=1000, required=False)
	parser.add_argument('--influxdb_retention_policy', type=str, default='', required=False)
	parser.add_argument('--verbose', type=bool, default=False, required=False)
	parser.add_argument('--statistics', type=bool, default=False, required=False)
	parser.add_argument('--configfile', type=str, default=None, required=False)
	return parser.parse_args()

if __name__ == '__main__':
	args = parse_args()
	main(args)
