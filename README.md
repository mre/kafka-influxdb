kafka-InfluxDB
==============

A Kafka consumer for InfluxDB.
All messages sent to Kafka on a certain topic will be relayed to influxdb. 
Supports influxdb version >= 0.9 (set the respective flag)

## Example Usage

    python kafka_influxdb.py --influxdb_host 127.0.0.1 --influxdb_port 8086

## Options

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
                           [--buffer_size BUFFER_SIZE]
                           [--influxdb_retention_policy RETENTION_POLICY]
                           [--verbose BOOLEAN]
                           [--statistics BOOLEAN]


## TODOs

* flush buffer if not full but some period has elapsed (safety net for low frequency input)
* offset management
* retention policy is not sent
* support config files and maybe remove flags
* add remaining tags
* create error log
