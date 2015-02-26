from kafka.client import KafkaClient
from kafka.consumer import SimpleConsumer
from influxdb import InfluxDBClient
import json
import argparse
from collections import defaultdict

DB_VERSION_DEFAULT = 0.8
DB_VERSION_APICHANGE = 0.9

class InfluxDBData09(object):
	def __init__(self, database, retention_policy):
		self.database = database
		self.retentionPolicy = retention_policy
		self.points = []

	def add_points(self, points):
		self.points = self.points + points

	def to_json(self):
		return json.dumps(self.__dict__)

	def reset(self):
		self.points = []

class InfluxDBData(object):
	def __init__(self, name, columns):
		self.name = name	
		self.columns = columns
		self.points = []

	def add_point(self, *point):
		self.points.append(list(point))
	
	def to_json(self):
		return json.dumps([self.__dict__])

	def reset(self):
		self.points = []

def main(config):
	# Kafka settings
	kafka = KafkaClient("{0}:{1}".format(config.kafka_host, config.kafka_port))

	client = InfluxDBClient(config.influxdb_host,
				config.influxdb_port,
				config.influxdb_user,
				config.influxdb_password,
				config.influxdb_dbname)

	try:
		db_version = float(config.influxdb_version)
		version_0_9 = db_version >= DB_VERSION_APICHANGE
	except:
		version_0_9 = False

	# Consume messages
	consumer = SimpleConsumer(kafka, config.kafka_group, config.kafka_topic)
	
	if version_0_9:
		stats = InfluxDBData09(config.influxdb_dbname, config.influxdb_retention_policy)
	else:
		stats = InfluxDBData(config.influxdb_data_name, config.influxdb_columns)
	i = 0
	for message in consumer:
		i = i + 1
		if config.verbose:
			print "Loop %d of buffer size %d" % (i, config.buffer_size)
		val = message.message.value
		if version_0_9:
			stats.add_points(transform_to_0_9(val))
		else:
			stats.add_point(val)
		if i == config.buffer_size or config.buffer_size == 0:
			data = stats.to_json()
			print "bar"
			print  data # TODO remove
			client.write_points(data)
			stats.reset()
			exit() # todo remove
	kafka.close()

def transform_to_0_9(kafka_message): # TODO add error handling
	#print "Original kafka input:" # TODO remove
	#print kafka_message # TODO remove
	results = []
	for json_obj in json.loads(kafka_message):
		#print "Tuple element: "  # TODO remove
		#print json_obj # TODO remove
		timestamp = json_obj['time'] # todo might need conversion? is a float!
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
			new_point["timestamp"] = int(timestamp)
			new_point["tags"] = tags
			# TODO append i indexed dstype and dsvalue if not empty to tags and check that that really works
			new_point["fields"] = {"value" : json_obj['values'][i]}
			results.append(new_point)
			
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
	parser.add_argument('--influxdb_retention_policy', type=str, default='365d', required=False)
	parser.add_argument('--verbose', type=bool, default=False, required=False)
	return parser.parse_args()

if __name__ == '__main__':
	args = parse_args()
	main(args)
