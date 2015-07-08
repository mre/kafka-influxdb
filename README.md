Kafka-InfluxDB
==============

A Kafka consumer for InfluxDB written in Python.  
All messages sent to Kafka on a certain topic will be relayed to Influxdb.
Supports Influxdb 0.8.x and 0.9.x.

## Usage

### Starting inside a container

The most convenient way to get started is running this inside a Docker container like so:

    docker build -t mre/kafka_influxdb .
    docker run -it --rm mre/kafka_influxdb

To run a simple test setup, you can run a collectd -> kafka -> kafka_influxdb -> influxdb toolchain with the following command:

    docker-compose up

### Starting manually

If you want to run a local instance, you can do so with the following commands:

    pip install -r requirements.txt
    # You might need to adjust the config.yaml
    python kafka_influxdb.py -c config.yaml


## Supported input and output formats

### Input formats

* Graphite

### Output formats

* InfluxDB 0.9 and later
* InfluxDB 0.8

### Extending

You can write a custom encoder to support any other format (e.g. Protobuf). Look at the examples in the `encoder` folder to get started.

## Configuration

    kafka_influxdb.py [-h] [--kafka_host KAFKA_HOST]
                           [--kafka_port KAFKA_PORT]
                           [--kafka_topic KAFKA_TOPIC]
                           [--kafka_group KAFKA_GROUP]
                           [--influxdb_host INFLUXDB_HOST]
                           [--influxdb_port INFLUXDB_PORT]
                           [--influxdb_user INFLUXDB_USER]
                           [--influxdb_password INFLUXDB_PASSWORD]
                           [--influxdb_dbname INFLUXDB_DBNAME]
                           [--influxdb_data_name INFLUXDB_DATA_NAME]
                           [--influxdb_columns INFLUXDB_COLUMNS]
                           [--influxdb_version DB_VERSION]
                           [--influxdb_retention_policy RETENTION_POLICY]
                           [--buffer_size BUFFER_SIZE]
                           [--verbose BOOLEAN]
                           [--statistics BOOLEAN]
                           [--configfile CONFIG_FILE]

Command line settings have precedence over config file provided settings. See the sample at `config.yaml` to get an idea on the format.


## Todo
* flush buffer if not full but some period has elapsed (safety net for low frequency input)
* Provide environment variables for docker
