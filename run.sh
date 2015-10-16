#!/usr/bin/env bash

KAFKA_HOST="kafka"
KAFKA_PORT=9092
INFLUXDB_HOST="influxdb"
INFLUXDB_PORT=8086

while true
do
  echo "Waiting for Kafka connection at $KAFKA_HOST:$KAFKA_PORT. This may take a while..."
  timeout 1 bash -c "cat < /dev/null > /dev/tcp/$KAFKA_HOST/$KAFKA_PORT"
  if [ $? -eq 0 ]; then
    break
  fi
  sleep 2
done


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
  kafka_influxdb -v -c config_example.yaml
else
  echo "Starting performance benchmark"
  kafka_influxdb -v -c config_example.yaml --benchmark
fi
