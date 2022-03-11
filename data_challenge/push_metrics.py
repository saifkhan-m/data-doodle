from json import dumps
from kafka import KafkaProducer

class PushMetrics():
    def __init__(self):
        self.producer = KafkaProducer(bootstrap_servers=['localhost:9092'],
                                 value_serializer=lambda x: dumps(x).encode('utf-8'))
    def push(self, msg):
        self.producer.send('metrics', value=msg)
