from config import cfg
import kafka
import uuid
import json
import random


class KafkaSender:
    def __init__(self):
        self.producer = kafka.KafkaProducer(bootstrap_servers=cfg.kafka_hosts, )

    def generate_message(self):
        product = random.choice(cfg.products)
        message = {
            'Message_Id': str(uuid.uuid4()),
            'Code': product['Code'],
            'Product': product['Name'],
            'Price': product['Price'],
        }
        return json.dumps(message).encode()

    def send(self):
        self.producer.send(
            'input-topic',
            value=self.generate_message(),
        )
        self.producer.flush()
