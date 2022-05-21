import kafka
import uuid
import json


class KafkaSender:
    def __init__(self):
        self.producer = kafka.KafkaProducer(bootstrap_servers=['localhost:29092'], )

    def generate_message(self):
        message = {'message_Id': str(uuid.uuid4()),
                   'text': f'Hello World', }
        return json.dumps(message).encode()

    def send(self):
        self.producer.send('input-topic',
                           value=self.generate_message(), )
        self.producer.flush()


kfk = KafkaSender()