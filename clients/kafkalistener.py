# -*- coding: utf-8 -*-

from kafka.consumer import SimpleConsumer
import time

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
				self.stats.add_point(val)
				if self.config.statistics:
					self.count_datapoints = self.count_datapoints + 1
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