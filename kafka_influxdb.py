from kafka.client import KafkaClient
from kafka.consumer import SimpleConsumer
from influxdb import InfluxDBClient # TODO import dynamically. If version 0.9 we have different requirements!
import json
import argparse
import time
import yaml
from collections import defaultdict

DB_VERSION_DEFAULT = 0.8
DB_VERSION_APICHANGE = 0.9

class InfluxDBData09(object):
	def __init__(self):
		self.points = []

	def add_points(self, points):
		self.points = self.points + points


	def reset(self):
		self.points = []

class InfluxDBData(object):
	def __init__(self, name, columns):
		self.name = name	
		self.columns = columns
		self.points = []

	def add_point(self, *point):
		self.points.append(list(point))
	
	def reset(self):
		self.points = []



class KafkaListener(object):
	

	def __init__(self, kafka_client, influxdb_client, config):
		self.kafka = kafka_client
		self.client = influxdb_client
		self.config = config
		self.consumer = SimpleConsumer(self.kafka, self.config.kafka_group, self.config.kafka_topic)
		

		try:
			db_version = float(self.config.influxdb_version)
			self.version_0_9 = db_version >= DB_VERSION_APICHANGE
		except:
			self.version_0_9 = False
		if self.version_0_9:
			self.stats = InfluxDBData09()
		else:
			self.stats = InfluxDBData(self.config.influxdb_data_name, self.config.influxdb_columns)

	def listen(self):
		
		i = 0
		self.count_flush = 0
		self.count_kafka = 0
		self.count_datapoints = 0
		self.aborted = False
		starttime = get_millis()
		
		log( "Listening.")

		for message in self.consumer:
			i = i + 1
			
			val = message.message.value
			if self.version_0_9:
				transformed = transform_to_0_9(val)
				self.stats.add_points(transformed)
				if self.config.statistics:
					self.count_datapoints = self.count_datapoints + len(transformed)	
			else:
				stats.add_point(val)
			if i == self.config.buffer_size or self.config.buffer_size == 0 or self.aborted:
				self.flush()				
				if self.config.statistics:
					self.calculate_statistics(starttime, i)
				i = 0
				self.stats.reset()
			if self.aborted:
				break
				
		# TODO close consumer?
		self.kafka.close()

	def calculate_statistics(self, starttime, i):
		self.count_kafka = self.count_kafka + i	
		self.count_flush = self.count_flush + 1
		now = get_millis()
		time_elapsed_ms = (now - starttime)
		if self.config.verbose:
			log( "Time elapsed: %d - %d = %d" % (now, starttime, time_elapsed_ms))
		kafka_per_ms = (float(self.count_kafka) / time_elapsed_ms)
		kafka_per_sec = kafka_per_ms * 1000
		if self.config.verbose:
			log( "Count kafka: %d / %d = %d * 1000 = %d" % (self.count_kafka, time_elapsed_ms , kafka_per_ms, kafka_per_sec))
		log( "Flush %d. Buffer size %d. Parsed %d kafka mes. into %d datapoints. Speed: %d kafka mes./sec" % (self.count_flush, self.config.buffer_size, self.count_kafka, self.count_datapoints, kafka_per_sec))

	def abort(self):
		self.aborted = True

	def flush(self):
		try:
			if self.version_0_9:
				data = self.stats.points		
			else:
				data = [self.stats.__dict__]
			self.client.write_points(data, "s", self.config.influxdb_dbname, self.config.influxdb_retention_policy)
			
		except Exception as inst:
			error_log("Exception caught while flushing: %s" % inst)

def main(config):
	if config.configfile is not None and config.configfile != u'':
		read_config_file(config)
		print "Updated config: " # TODO remove
		print config
		exit() # TODO remove

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
	print "Enter config loop with prefix %s" % prefix # TODO remove
	"""
	mappings = [ 	# TODO come up with a better way to do this. Maybe read from the dict itself
			('kafka','host'),
			('kafka','port'),
			('kafka','topic'),
			('kafka','group'),
			('influxdb','host'),
			('influxdb','port'), # TODO add others
			('statistics'),
			('verbose'),
			('buffer_size'),
		]
	"""
	for key, value in values.iteritems() :
		print key, value, type(value)
		if type(value) == type(dict()):
			set_config_values(config, value, "%s_" % key)
		elif value != u'':
			setattr(config, "%s%s" % (prefix, key), value)
			print "Setting %s to %s" % ("%s%s" % (prefix, key), value) # TODO remove
		
def log(msg):
	print msg # TODO
	
def error_log(msg, die=False):
	print msg # TODO
	if die:
		exit()

def get_millis():
	return int(round(time.time() * 1000))

def transform_to_0_9(kafka_message):
	results = []
	try:
		for json_obj in json.loads(kafka_message):
			timestamp = int(json_obj['time'])
			tags = {}
			tags['host'] = json_obj['host']
			if json_obj['plugin_instance'] != u'':
				tags['plugin_instance'] = json_obj['plugin_instance']
			if json_obj['type_instance'] != u'':
				tags['type_instance'] = json_obj['type_instance']
			if json_obj['type'] != u'':
				tags['type'] = json_obj['type']
			for i in range (0, len(json_obj['values'])):
				
				if json_obj['dstypes'][i] != u'':
					tags['ds_type'] = json_obj['dstypes'][i]
				else:
					del tags['ds_type'] #in case this has been set in a previous loop iteration
				if json_obj['dsnames'][i] != u'':
					tags['ds_name'] = json_obj['dsnames'][i]
				else:
					del tags['ds_name'] #in case this has been set in a previous loop iteration
				new_point = {"precision":"s"}
				new_point["name"] = json_obj['plugin']
				new_point["timestamp"] = timestamp
				new_point["tags"] = tags
				
				new_point["fields"] = {"value" : json_obj['values'][i]}
				results.append(new_point)
	except Exception as inst:
		error_log("Exception caught in json transformation: %s" % inst)
	return results

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
