# -*- coding: utf-8 -*-

class InfluxDBData(object):
	def __init__(self, name, columns):
		self.name = name	
		self.columns = columns
		self.points = []

	def add_point(self, *point):
		self.points.append(list(point))
	
	def reset(self):
		self.points = []