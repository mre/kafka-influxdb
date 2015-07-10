Kafka-InfluxDB
==============

A Kafka consumer for InfluxDB written in Python.  
All messages sent to Kafka on a certain topic will be relayed to Influxdb.  
Supports InfluxDB 0.9.x. For InfluxDB 0.8 support look check out the 0.3.0 tag.

## Usage

### Manual installation

If you want to run a local instance, you can do so with the following commands:

    pip install -r requirements.txt
    # You might need to adjust the config.yaml
    python kafka_influxdb.py -c config.yaml

### Starting inside a container

The most convenient way to get started is running this inside a Docker container like so:

    docker build -t mre/kafka_influxdb .
    docker run -it --rm mre/kafka_influxdb

To run a simple test setup, you can run a collectd -> kafka -> kafka_influxdb -> influxdb toolchain with the following command:

    docker-compose up

## Supported input and output formats

### Input formats

* Collectd Graphite, e.g. "mydatacenter.myhost.load.load.shortterm 0.45 1436357630"

### Output formats

* InfluxDB 0.9 line protocol output (e.g. `load_load_shortterm,datacenter=mydatacenter,host=myhost value="0.45" 1436357630`)
* InfluxDB 0.8 JSON output (deprecated)

### Extending

You can write a custom encoder to support any other format (even fancy things like Protobuf).  
Look at the examples in the `encoder` folder to get started.

## Configuration

usage: kafka_influxdb.py [-h] [--kafka_host KAFKA_HOST]
                         [--kafka_port KAFKA_PORT] [--kafka_topic KAFKA_TOPIC]
                         [--kafka_group KAFKA_GROUP]
                         [--influxdb_host INFLUXDB_HOST]
                         [--influxdb_port INFLUXDB_PORT]
                         [--influxdb_user INFLUXDB_USER]
                         [--influxdb_password INFLUXDB_PASSWORD]
                         [--influxdb_dbname INFLUXDB_DBNAME]
                         [--influxdb_retention_policy INFLUXDB_RETENTION_POLICY]
                         [--influxdb_time_precision INFLUXDB_TIME_PRECISION]
                         [--encoder ENCODER] [--buffer_size BUFFER_SIZE]
                         [-c CONFIGFILE] [-v]

A Kafka consumer for InfluxDB

optional arguments:
  -h, --help            show this help message and exit
  --kafka_host KAFKA_HOST
                        Hostname or IP of Kafka message broker (default:
                        localhost)
  --kafka_port KAFKA_PORT
                        Port of Kafka message broker (default: 9092)
  --kafka_topic KAFKA_TOPIC
                        Topic for metrics (default: test)
  --kafka_group KAFKA_GROUP
                        Kafka consumer group (default: my_group)
  --influxdb_host INFLUXDB_HOST
                        InfluxDB hostname or IP (default: localhost)
  --influxdb_port INFLUXDB_PORT
                        InfluxDB API port (default: 8086)
  --influxdb_user INFLUXDB_USER
                        InfluxDB username (default: root)
  --influxdb_password INFLUXDB_PASSWORD
                        InfluxDB password (default: root)
  --influxdb_dbname INFLUXDB_DBNAME
                        InfluXDB database to write metrics into (default:
                        metrics)
  --influxdb_retention_policy INFLUXDB_RETENTION_POLICY
                        Retention policy for incoming metrics (default:
                        default)
  --influxdb_time_precision INFLUXDB_TIME_PRECISION
                        Precision of incoming metrics. Can be one of 's', 'm',
                        'ms', 'u' (default: s)
  --encoder ENCODER     Input encoder which converts an incoming message to
                        dictionary (default: collectd_graphite_encoder)
  --buffer_size BUFFER_SIZE
                        Maximum number of messages that will be collected
                        before flushing to the backend (default: 1000)
  -c CONFIGFILE, --configfile CONFIGFILE
                        Configfile path (default: None)
  -v, --verbose         Show info and debug messages while running (default:
                        False)

Command line settings have precedence over config file provided settings. See the sample at `config.yaml` to get an idea on the format.

## TODO

* flush buffer if not full but some period has elapsed (safety net for low frequency input)
* Provide environment variables for docker
