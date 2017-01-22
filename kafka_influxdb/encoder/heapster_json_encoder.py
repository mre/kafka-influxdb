try:
    import ujson as json
except ImportError:
    import json

import logging

try:
    # Test for mypy support (requires Python 3)
    from typing import List, Text
except:
    pass

from datetime import datetime
from kafka_influxdb.encoder.escape_functions import influxdb_tag_escaper

class Encoder(object):
    """
    @see https://github.com/kubernetes/heapster/blob/master/metrics/sinks/kafka/driver.go
    
    Sample measurements:

    {
     "MetricsName":"memory/major_page_faults",
     "MetricsValue":{"value":56},
     "MetricsTimestamp":"2017-01-19T17:26:00Z",
     "MetricsTags":{"cluster":"c","container_name":"docker/9be430d3a1a28601292aebd76e15512d5471c630a7fa164d6a2a2fd9cbc19e3d","host_id":"10.58.9.95","hostname":"10.58.9.95","nodename":"10.58.9.95","type":"sys_container"}
    }    

    or
    
    {"MetricsName":"memory/usage",
    "MetricsValue":{"value":1036288},
    "MetricsTimestamp":"2017-01-19T17:26:00Z",
    "MetricsTags":{"cluster":"c","container_base_image":"gcr.io/google_containers/kube-dnsmasq-amd64:1.4","container_name":"dnsmasq","host_id":"10.58.9.96","hostname":"10.58.9.96",
            "labels":"k8s-app:kube-dns,pod-template-hash:4101612645","namespace_id":"a8bf368b-489b-11e6-91f3-005056923a7e","namespace_name":"kube-system","nodename":"10.58.9.96",
            "pod_id":"f7570b50-d637-11e6-bd3e-005056923a7e","pod_name":"kube-dns-4101612645-8pn6x","pod_namespace":"kube-system","type":"pod_container"}} 
    """
    
    def __init__(self):
        self.escape_tag = influxdb_tag_escaper()

    def encode(self, msg):
        # type: (bytes) -> List[Text]
        measurements = []

        try:
            entry = self.parse_line(msg.decode())
        except ValueError as e:
            logging.debug("Error in encoder: %s", e)
            return measurements
        
        try:                    
            measurement = entry["MetricsName"]
            tags = self.format_tags(entry)
            value = self.format_value(entry)
            time = self.format_time(entry)
            measurements.append(self.compose_data(measurement, tags, value, time))
        except Exception as e:
            logging.debug("Error in input data: %s. Skipping.", e)

        return measurements

    def parse_line(self, line):
        # return json.loads(line, {'precise_float': True})
        # for influxdb version > 0.9, timestamp is an integer
        return json.loads(line)

    # following methods are added to support customizing measurement name, tags much more flexible
    def compose_data(self, measurement, tags, value, time):
        data = "{0!s},{1!s} {2!s} {3!s}".format(measurement, tags, value, time)
        return data

    def format_tags(self, entry):
        tag = []
        tags = entry["MetricsTags"]
        if tags == '':
            return ''
                
        for kv in tags.items():
            # to avoid add None as tag value
            if kv[0] != '' and kv[1] != '':
                tag.append("{0!s}={1!s}".format(self.escape_tag(kv[0]), self.escape_tag(kv[1])))
                
        return ','.join(tag)

    def format_time(self, entry):
        d = datetime.strptime(entry['MetricsTimestamp'], '%Y-%m-%dT%H:%M:%SZ')
        return int((d-datetime(1970,1,1)).total_seconds())

    def format_value(self, entry):
        return "value={0!s}".format(entry['MetricsValue']["value"])