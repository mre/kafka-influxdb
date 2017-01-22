import unittest

from kafka_influxdb.encoder import heapster_json_encoder

class TestHeapsterJsonEncoder(unittest.TestCase):

    def setUp(self):
        self.encoder = heapster_json_encoder.Encoder()

    def testEncoder(self):
        msg = b'{ "MetricsName":"memory/major_page_faults","MetricsValue":{"value":56}, "MetricsTimestamp":"2017-01-19T17:26:00Z", "MetricsTags":{"container_name":"docker/9be430d3a1a28601292aebd76e15512d5471c630a7fa164d6a2a2fd9cbc19e3d"} } '
        encoded_message = self.encoder.encode(msg)        
        expected_msg = ['memory/major_page_faults,container_name=docker/9be430d3a1a28601292aebd76e15512d5471c630a7fa164d6a2a2fd9cbc19e3d value=56 1484846760']       
        self.assertEqual(encoded_message, expected_msg)