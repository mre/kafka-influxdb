# Kafa-InfluxDB Encoders

These classes are used to convert from an input message format to the internal format of InfluxDB:
To write your own encoder for an unsupported format, do the following:

```python
class Encoder(object):
  def encode(self, msg):
    """
    Transfer msg into the internal InfluxDB v0.9 line protocol format
    See https://influxdb.com/docs/v0.9/write_protocols/line.html

    In general, a line consists of three parts:
    [key] [fields] [timestamp]

    Some output examples:
    cpu,host=server01,region=uswest value=1.0 1434055562000000000
    cpu,host=server02,region=uswest value=3.0 1434055562000010000
    temperature,machine=unit42,type=assembly internal=32,external=100 1434055562000000035
    temperature,machine=unit143,type=assembly internal=22,external=130 1434055562005000035

    # line with commas
    cpu\,01,host=serverA,region=us-west value=1.0 1434055562000000000

    # line with spaces
    cpu,host=server\ A,region=us\ west value=1.0 1434055562000000000

    """
```
