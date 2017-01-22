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
    @see https://github.com/kubernetes/heapster/blob/master/events/sinks/kafka/driver.go
    
    Sample events:
   {
                     
      "EventValue": "{\n 
              \"metadata\":
                         {\n  \"name\": \"jslave-golang-1711858954-g9rbc.149b8219c4dd21de\",\n  
                         \"namespace\": \"kube-system\",\n  
                         \"selfLink\": \"/api/v1/namespaces/kube-system/events/jslave-golang-1711858954-g9rbc.149b8219c4dd21de\",\n 
                          \"uid\": \"2246f36f-df1f-11e6-bd3e-005056923a7e\",\n  
                          \"resourceVersion\": \"21506467\",\n  
                          \"creationTimestamp\": \"2017-01-20T14:45:49Z\"\n },\n 
                          
              \"involvedObject\": 
                      {\n  \"kind\": \"Pod\",
                       \n  \"namespace\": \"kube-system\",\n 
                    \"name\": \"jslave-golang-1711858954-g9rbc\",\n  
                    \"uid\": \"20e28ba6-df1f-11e6-bd3e-005056923a7e\",\n  
                    \"apiVersion\": \"v1\",\n 
                     \"resourceVersion\": \"21506452\",\n  
                    \"fieldPath\": \"spec.containers{golang}\"\n 
                    },
              \n \"reason\": \"Started\",\n 
              \"message\": \"Error syncing pod, skipping: failed to "StartContainer" for "backup" with ImagePullBackOff: "Back-off pulling image \\"10.58.9.201:5000/dc/etcd-operator:latest\\""\n\",\n
              \"source\": 
                     {\n  \"component\": \"kubelet\",\n  \"host\": \"10.58.9.212\"\n },
                    \n 
              \"firstTimestamp\": \"2017-01-20T14:45:49Z\",\n \"lastTimestamp\": \"2017-01-20T14:45:49Z\",
              \n \"count\": 1,\n \"type\": \"Normal\"\n}",
        "EventTimestamp": "2017-01-20T14:45:49Z",
        "EventTags": {
            "cluster": "c",
            "eventID": "2246f36f-df1f-11e6-bd3e-005056923a7e",
            "hostname": "10.58.9.212",
            "pod_id": "20e28ba6-df1f-11e6-bd3e-005056923a7e",
            "pod_name": "jslave-golang-1711858954-g9rbc"
        } 
    }              
     """
    
    def __init__(self):
        self.escape_tag = influxdb_tag_escaper()

    def encode(self, msg):
        # type: (bytes) -> List[Text]
        measurements = []
        try:
            entry = Encoder.parse_line(msg.decode())
        except ValueError as e:
            logging.debug("Error in encoder: %s", e)
            return measurements
        
        try:
            measurement = "events"
            tags_value = self.format_tags_value(entry)
            time = self.format_time(entry)
            measurements.append(self.compose_data(measurement, tags_value, time))
        except Exception as e:
            logging.debug("Error in input data: %s. Skipping.", e)

        return measurements

    @staticmethod
    def parse_line(line):
        # return json.loads(line, {'precise_float': True})
        # for influxdb version > 0.9, timestamp is an integer
        return json.loads(line)

    # following methods are added to support customizing measurement name, tags much more flexible
    def compose_data(self, measurement, tags_value, time):
        data = "{0!s},{1!s} {2!s}".format(measurement, tags_value, time)
        return data

    def format_tags_value(self, entry):
        tag = []
        ev = Encoder.parse_line(entry["EventValue"])
        obj = ev["involvedObject"]
        tag.append("kind={0!s}".format(self.escape_tag(obj["kind"])))
        tag.append("namespace_name={0!s}".format(self.escape_tag(obj["namespace"])))
        tag.append("object_name={0!s}".format(self.escape_tag(obj["name"])))

        tag.append("reason={0!s}".format(self.escape_tag(ev["reason"] )))
        
        tags = entry["EventTags"]
        if tags.get("hostname"):
            tag.append('hostname="{0!s}"'.format(self.escape_tag(tags["hostname"])))
      
        tag_str = ','.join(tag) 
        msg = ev["message"].replace('\\"', '"').replace("\n", '').replace('"', '\\"')
        value = 'message="{0!s}"'.format(msg)
        return "{0!s} {1!s}".format(tag_str, value)
        
    def format_time(self, entry):
        d = datetime.strptime(entry['EventTimestamp'], '%Y-%m-%dT%H:%M:%SZ')
        return int((d-datetime(1970,1,1)).total_seconds())