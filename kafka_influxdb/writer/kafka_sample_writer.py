import kafka
import kafka.common
import random
import logging
import time


class KafkaWriterException(Exception):
    pass


class KafkaSampleWriter(object):
    """
    KafkaSampleWriter can be used to write sample messages into Kafka for
    benchmark purposes
    """

    def __init__(self, host, port, topic):
        self.kafka_client = self._create_kafka_client(host, port)
        self.topic = topic

        self.sample_messages = [
            b"""26f2fc918f50.load.load.shortterm 0.05 1436357630
            26f2fc918f50.load.load.midterm 0.05 1436357630
            26f2fc918f50.load.load.longterm 0.05 1436357630""",
            b"26f2fc918f50.cpu-0.cpu-user 30364 1436357630",
            b"26f2fc918f50.memory.memory-buffered 743657472 1436357630"
        ]

    def produce_messages(self, batches=1000, batch_size=1000):
        """
        Produce Kafka sample messages
        :param batches: number of message batches
        :param batch_size: messages per batch
        :return:
        """
        partitions = self._get_partitions(self.topic)
        if not partitions:
            raise KafkaWriterException("No partitions found for %s" % self.topic)

        kafka_messages = self._create_random_messages(self.sample_messages, batch_size)
        kafka_requests = [self._create_request(self.topic, p, kafka_messages) for p in partitions]
        self._send_request_batches(kafka_requests, batches, batch_size)

    def _send_request_batches(self, kafka_requests, batches, batch_size):
        total_messages = batches * batch_size
        for i in range(batches):
            self._send_requests(kafka_requests)
            logging.info("Sent %s out of %s messages", i * batch_size, total_messages)
        self.kafka_client.close()

    def _send_requests(self, requests):
        try:
            self.kafka_client.send_produce_request(payloads=requests, fail_on_error=True)
        except kafka.common.UnknownTopicOrPartitionError as e:
            logging.error(e)
            time.sleep(1)
            self.kafka_client.close()

    def _get_partitions(self, topic):
        return self.kafka_client.get_partition_ids_for_topic(topic)

    @staticmethod
    def _create_kafka_client(host, port):
        logging.info("Connecting to Kafka broker at %s:%s", host, port)
        return kafka.KafkaClient("{}:{}".format(host, port))

    @staticmethod
    def _create_random_messages(messages, count):
        return [kafka.create_message(random.choice(messages)) for _ in range(count)]

    @staticmethod
    def _create_request(topic, partition, messages):
        return kafka.common.ProduceRequest(topic=topic, partition=partition, messages=messages)
