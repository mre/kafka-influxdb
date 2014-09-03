from kafka.client import KafkaClient
from kafka.consumer import SimpleConsumer
from kafka.producer import SimpleProducer, KeyedProducer
from influxdb import InfluxDBClient
import json
import argparse

class InfluxDBData(object):
	def __init__(self, name, columns):
		self.name = name	
		self.columns = columns
		self.points = []

	def add_point(self, *point):
		self.points.append(list(point))
	
	def to_json(self):
		return json.dumps(self.__dict__)

def main(config):
	# Kafka settings
	kafka = KafkaClient("{0}:{1}".format(config.kafka_host, config.kafka_port))

	client = InfluxDBClient(config.influxdb_host,
				config.influxdb_port,
				config.influxdb_user,
				config.influxdb_password,
				config.influxdb_dbname)

	stats = InfluxDBData(config.influxdb_data_name, config.influxdb_columns)

	# Consume messages
	consumer = SimpleConsumer(kafka, config.kafka_group, config.kafka_topic)
	for message in consumer:
		val = message.message.value
		stats.add_point(val)
		data = json.dumps([stats.__dict__])
		client.write_points(data)
	kafka.close()

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
	return parser.parse_args()

if __name__ == '__main__':
	args = parse_args()
	main(args)
