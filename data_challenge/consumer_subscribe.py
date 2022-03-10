from kafka import KafkaConsumer
from json import loads
from postProcessing import roundTime, process_list_uids

from datetime import datetime

consumer = KafkaConsumer(
    'doodle_data',
     bootstrap_servers=['localhost:9092'],
     auto_offset_reset='earliest',
     enable_auto_commit=True,
     group_id=None,
    consumer_timeout_ms=5000,
     value_deserializer = lambda x: loads(x.decode('utf-8'))
     )

print("loaded")

ts_min_lst= []
ts_hr_lst=[]
time_stmp_min=0
time_stmp_hr=0

for message in consumer:
    if time_stmp_min==0 and time_stmp_hr==0:
        time_stmp_min=message.value['ts']
        time_stmp_hr=roundTime(dt=datetime.utcfromtimestamp(message.value['ts']), roundTo=10*60)
        print(time_stmp_hr)
    
    
    if time_stmp_min != message.value['ts'] and False:
        process_list_uids(time_stmp_min,ts_min_lst, duraton='minute')
        ts_min_lst= []
        time_stmp_min= message.value['ts']

    message_ts_hr=roundTime(dt=datetime.utcfromtimestamp(message.value['ts']), roundTo=10*60)
    #print(message_ts_hr)
    if time_stmp_hr != message_ts_hr:
        print(time_stmp_hr, message_ts_hr)
        process_list_uids(time_stmp_hr,ts_hr_lst,  duraton='hour')
        ts_hr_lst= []
        time_stmp_hr= message_ts_hr

    #ts_min_lst.append(message.value['uid'])
    ts_hr_lst.append(message.value['uid'])

print("done")
consumer.close()
def freq_count():
    pass

# while True:
#     raw_messages = consumer.poll(timeout_ms=1000)
#     print(raw_messages)

 #message = message.value

    # print("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
    #                                      message.offset, message.key,
    #                                      message.value['ts']))