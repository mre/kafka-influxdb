# -*- coding: utf-8 -*-

class InfluxDBData09(object):
	def __init__(self):
		self.points = []

	def add_points(self, points):
		self.points = self.points + points

	def reset(self):
		self.points = []
