from kafka import KafkaClient, create_message
from kafka.protocol import KafkaProtocol
from kafka.common import ProduceRequest
import random
import logging

class KafkaSampleWriter(object):
    """
    KafkaSampleWriter can be used to write sample messages into Kafka for
    benchmark purposes
    """

    def __init__(self, config, batches = 1000, batch_size = 1000):
        self.config = config
        self.batches = batches
        self.batch_size = batch_size
        # Sample messages for benchmark
        self.sample_messages = [
            """26f2fc918f50.load.load.shortterm 0.05 1436357630
            26f2fc918f50.load.load.midterm 0.05 1436357630
            26f2fc918f50.load.load.longterm 0.05 1436357630""",
            "26f2fc918f50.cpu-0.cpu-user 30364 1436357630",
            "26f2fc918f50.memory.memory-buffered 743657472 1436357630"
        ]

    def produce_messages(self):
        """
        Produce sample messages
        """
        # TODO: Support different kafka port
        kafka = KafkaClient(self.config.kafka_host)

        total_messages = self.batches * self.batch_size
        messages_batch = [create_message(random.choice(self.sample_messages)) for r in range(self.batch_size)]

        for i in range(self.batches):
            # TODO: Support writing to all partitions
            req = ProduceRequest(topic=self.config.kafka_topic, partition=0, messages=messages_batch)
            resps = kafka.send_produce_request(payloads=[req], fail_on_error=True)
            sent_messages = i * self.batch_size
            logging.info('Created %s out of %s sample messages', sent_messages, total_messages)
        kafka.close()
