#!/usr/bin/env bash

KAFKA_HOST="kafka"
KAFKA_PORT=9092
KAFKA_TOPIC="metrics"

while true
do
  echo "Waiting for Kafka connection at $KAFKA_HOST:$KAFKA_PORT. This may take a while..."
  timeout 1 bash -c "cat < /dev/null > /dev/tcp/$KAFKA_HOST/$KAFKA_PORT"
  if [ $? -eq 0 ]; then
    break
  fi
  sleep 2
done

kafkacat -P -l -T -t ${KAFKA_TOPIC} -b ${KAFKA_HOST}:${KAFKA_PORT} "$@"

