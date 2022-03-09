from kafka import KafkaConsumer
from json import loads

consumer = KafkaConsumer(
    'doodle_data',#'quickstart-events',
     bootstrap_servers=['localhost:9092'],
     auto_offset_reset='earliest',
     enable_auto_commit=False,
     group_id=None
     )
print('loaded')
for message in consumer:
    print(message)
    message = message.value
    break
consumer.close()