from kafka.client import KafkaClient
from kafka.consumer import SimpleConsumer
from influxdb import InfluxDBClient # TODO import dynamically. If version 0.9 we have different requirements!
import json
import argparse
import time
from collections import defaultdict

DB_VERSION_DEFAULT = 0.8
DB_VERSION_APICHANGE = 0.9



#	python kafka_influxdb.py --kafka_topic perfmonspring1 --influxdb_user root --influxdb_password root --influxdb_dbname mydb --influxdb_version 0.9 --kafka_host 10.1.3.234 --influxdb_host springfield02.local --buffer_size 2
# TODO remove ^


class InfluxDBData09(object):
	def __init__(self, database, retention_policy):
		self.database = database
		if retention_policy != u'':
			self.retentionPolicy = retention_policy
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
			self.stats = InfluxDBData09(self.config.influxdb_dbname, self.config.influxdb_retention_policy)
		else:
			self.stats = InfluxDBData(self.config.influxdb_data_name, self.config.influxdb_columns)

	def listen(self):
		
		i = 0
		self.count_flush = 0
		self.count_kafka = 0
		self.count_datapoints = 0
		self.aborted = False
		starttime = get_millis()
		
		print "Listening." # TODO remove

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
			print "Time elapsed: %d - %d = %d" % (now, starttime, time_elapsed_ms)
		kafka_per_ms = (float(self.count_kafka) / time_elapsed_ms)
		kafka_per_sec = kafka_per_ms * 1000
		if self.config.verbose:
			print "Count kafka: %d / %d = %d * 1000 = %d" % (self.count_kafka, time_elapsed_ms , kafka_per_ms, kafka_per_sec)
		print "Flush %d. Buffer size %d. Parsed %d kafka mes. into %d datapoints. Speed: %d kafka mes./sec" % (self.count_flush, self.config.buffer_size, self.count_kafka, self.count_datapoints, kafka_per_sec)

	def abort(self):
		self.aborted = True

	def flush(self):
		if self.version_0_9:
			data = self.stats.points		
		else:
			data = [self.stats.__dict__]
		self.client.write_points(data)


def main(config):
	# Kafka settings
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
		error_log("Received Ctrl-C. Shutdown")
		listener.abort()

	
def error_log(msg):
	print msg # TODO

def get_millis():
	return int(round(time.time() * 1000))

def transform_to_0_9(kafka_message):
	results = []
	for json_obj in json.loads(kafka_message):
		try:
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
				# TODO check that range is defined correctly (borders)
				new_point = {"precision":"s"}
				new_point["name"] = json_obj['plugin']
				new_point["timestamp"] = timestamp
				new_point["tags"] = tags
				# TODO append i indexed dstype and dsvalue if not empty to tags and check that that really works
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
	return parser.parse_args()

if __name__ == '__main__':
	args = parse_args()
	main(args)
