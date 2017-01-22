import unittest

from kafka_influxdb.encoder import heapster_event_json_encoder

class TestHeapsterEventJsonEncoder(unittest.TestCase):

    def setUp(self):
        self.encoder = heapster_event_json_encoder.Encoder()

    def testEncoder(self):
        msg = b'{"EventValue":"{\\n \\"metadata\\": {\\n  \\"name\\": \\"etcd-operator-562633149-vvr85.149bd41846d603d4\\",\\n \\"namespace\\": \\"default\\",\\n  \\"selfLink\\":  \\"/api/v1/namespaces/default/events/etcd-operator-562633149-vvr85.149bd41846d603d4\\",\\n  \\"uid\\":   \\"09f904cd-dff1-11e6-bd3e-005056923a7e\\",\\n  \\"resourceVersion\\": \\"21782526\\",\\n  \\"creationTimestamp\\":     \\"2017-01-21T15:48:22Z\\"\\n },\\n \\"involvedObject\\": {\\n  \\"kind\\": \\"Pod\\",\\n  \\"namespace\\":\\"default\\",\\n  \\"name\\": \\"etcd-operator-562633149-vvr85\\",\\n \\"uid\\":\\"a5f12e21-de53-11e6-bd3e-005056923a7e\\",\\n  \\"apiVersion\\": \\"v1\\",\\n  \\"resourceVersion\\":\\"21339961\\",\\n  \\"fieldPath\\": \\"spec.containers{etcd-operator}\\"\\n },\\n \\"reason\\": \\"BackOff\\",\\n\\"message\\": \\"Back-off pulling image \\\\\\"10.58.9.201:5000/dc/etcd-operator:latest\\\\\\"\\",\\n \\"source\\":{\\n  \\"component\\": \\"kubelet\\",\\n  \\"host\\": \\"10.58.9.212\\"\\n },\\n \\"firstTimestamp\\":\\"2017-01-21T15:48:22Z\\",\\n \\"lastTimestamp\\": \\"2017-01-22T07:10:28Z\\",\\n \\"count\\": 3955,\\n \\"type\\": \\"Normal\\"\\n}","EventTimestamp":"2017-01-22T07:10:28Z","EventTags":{"eventID":"09f904cd-dff1-11e6-bd3e-005056923a7e","hostname":"10.58.9.212","pod_id":"a5f12e21-de53-11e6-bd3e-005056923a7e","pod_name":"etcd-operator-562633149-vvr85"}}'
        expected_msg = ['events,kind=Pod,namespace_name=default,object_name=etcd-operator-562633149-vvr85,reason=BackOff,hostname="10.58.9.212" message="Back-off pulling image \\"10.58.9.201:5000/dc/etcd-operator:latest\\"" 1485069028']
        encoded_message = self.encoder.encode(msg)
        self.assertEqual(encoded_message, expected_msg)