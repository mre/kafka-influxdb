#!/usr/bin/env bash

INFLUXDB_HOST="influxdb"
INFLUXDB_PORT=8086

while true
do
  echo "Waiting for InfluxDB connection at $INFLUXDB_HOST:$INFLUXDB_PORT. This may take a while..."
  curl --silent -G "http://$INFLUXDB_HOST:$INFLUXDB_PORT/query" --data-urlencode "q=SHOW DATABASES" > /dev/null
  if [ $? -eq 0 ]; then
    break
  fi
  sleep 2
done

if [ -z "$BENCHMARK" ]; then
  echo "Starting to consume messages"
  kafka_influxdb -c config.yaml
else
  echo "Starting performance benchmark"
  kafka_influxdb --benchmark --kafka_host kafka --kafka_topic benchmark
fi
