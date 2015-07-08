from collections import defaultdict
import argparse
import yaml
import logging
import importlib
from reader import kafka_reader
from writer import influxdb_writer

class KafkaInfluxDB(object):
	def __init__(self, config):
		""" Setup """
		if config.verbose:
			logging.getLogger().setLevel(logging.DEBUG)

		self.config = config
		if config.configfile:
			logging.debug("Reading", config.configfile)
			values = self.parse_configfile(config.configfile)
			self.set_config_values(values)
		else:
			logging.info("Using default configuration")

		self.input_encoder = self.load_encoder(config.encoder_input)
		self.reader = kafka_reader.KafkaReader(config.kafka_host,
										config.kafka_port,
										config.kafka_group,
										config.kafka_topic)

		self.output_encoder = self.load_encoder(config.encoder_output)
		self.writer = influxdb_writer.InfluxDBWriter(config.influxdb_host,
										config.influxdb_port,
										config.influxdb_user,
										config.influxdb_password,
										config.influxdb_dbname,
										config.influxdb_retention_policy,
										config.influxdb_time_precision)

		self.buffer = []


	def consume(self):
		""" Run loop. Consume messages from reader, convert it to the output format and write with writer """
		logging.info("Listening for messages on kafka topic ", self.config.kafka_topic)
		try:
			for index, raw_message in enumerate(self.reader.read(), 1):
				self.buffer.append(self.input_encoder.encode(raw_message))
				if index % self.config.buffer_size == 0:
					self.flush()
		except KeyboardInterrupt:
			logging.info("Shutdown")

	def flush(self):
		""" Flush values with writer """
		try:
			self.writer.write(self.buffer)
			self.buffer = []
			print "flush"
			exit(-1)
		except Exception, e:
			logging.warning(e)

	def load_encoder(self, encoder_name):
		""" Creates an instance of the given encoder """
		encoder_module = importlib.import_module("encoder." + encoder_name)
		encoder_class = getattr(encoder_module, "Encoder")
		return encoder_class()

	def parse_configfile(self, configfile):
		""" Read settings from file """
		values = None
		with open(configfile) as f:
			try:
				return yaml.safe_load(f)
			except Exception, e :
				logging.fatal("Could not load default config file: ", e)
				exit(-1)

	def set_config_values(self, values, prefix = ""):
		""" Overwrite default configs with custom values """
		for key, value in values.iteritems() :
			if type(value) == type(dict()):
				self.set_config_values(value, "%s_" % key)
			elif value != u'':
				setattr(self.config, "%s%s" % (prefix, key), value)

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
	parser.add_argument('--influxdb_retention_policy', type=str, default=None, required=False)
	parser.add_argument('--influxdb_time_precision', type=str, default="s", required=False)
	parser.add_argument('--encoder_input', type=str, default='echo_encoder', required=False)
	parser.add_argument('--encoder_output', type=str, default='influxdb09_encoder', required=False)
	parser.add_argument('--buffer_size', type=int, default=1000, required=False)
	parser.add_argument('-c', '--configfile', type=str, default=None, required=False)
	parser.add_argument('-v', '--verbose', help="increase output verbosity", action="store_true")

	return parser.parse_args()

if __name__ == '__main__'	:
	config = parse_args()
	client = KafkaInfluxDB(config)
	# Enter run loop
	client.consume()
