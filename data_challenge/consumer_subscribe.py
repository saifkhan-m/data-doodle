from kafka import KafkaConsumer
from json import loads
from postProcessing import roundTime, process_list_uids, convert_to_unix_time, process_list_uids_hll
from datetime import datetime
from push_metrics import PushMetrics
import time
import hyperloglog
from memory_profiler import memory_usage

def create_consumer():
    consumer = KafkaConsumer(
        'doodle_data',
         bootstrap_servers=['localhost:9092'],
         auto_offset_reset='earliest',
         enable_auto_commit=True,
         group_id=None,
        consumer_timeout_ms=5000,
         value_deserializer = lambda x: loads(x.decode('utf-8'))
         )
    return consumer


def close_everything(consumer, performance_file):
    consumer.close()
    performance_file.close()


def consume_messages(consumer, pushToTopic):
    ts_min_lst= []
    ts_hr_lst=[]
    time_stmp_min=0
    time_stmp_hr=0
    count = 0
    start = time.time()
    cm_time= time.time()
    performance_file = open("performance_file.txt", "w")
    for i, message in enumerate(consumer):

        '''
            Initialise the timestamps for different durations
        '''
        if time_stmp_min==0 and time_stmp_hr==0:

            ''' Initialise for 1 minute '''
            time_stmp_min=message.value['ts']

            ''' Initialise for 10 minutes. Can change the value of miutes by changing the value of roundTo in function '''
            ## postProcessing.roundTime()
            time_stmp_hr=roundTime(dt=datetime.utcfromtimestamp(message.value['ts']), roundTo=10*60)


        '''
            Storing the messages in list for the duration of 1 minute. Then processing it for total and unique users.
        '''

        if time_stmp_min != message.value['ts'] and False:
            process_list_uids(time_stmp_min,message.value['ts'], ts_min_lst, pushToTopic, duraton='minute')
            ts_min_lst= []
            time_stmp_min= message.value['ts']

        ''' 
            Storing the messages in list for the duration of 10 minute. Then processing it for total and unique users
        '''
        message_ts_hr=roundTime(dt=datetime.utcfromtimestamp(message.value['ts']), roundTo=10*60)
        if time_stmp_hr != message_ts_hr:
            #print(time_stmp_hr, message_ts_hr)
            process_list_uids(convert_to_unix_time(time_stmp_hr), convert_to_unix_time(message_ts_hr), ts_hr_lst, pushToTopic, duraton='10 minutes')
            ts_hr_lst= []
            time_stmp_hr= message_ts_hr

        #ts_min_lst.append(message.value['uid'])
        ts_hr_lst.append(message.value['uid'])
        count+=1

        if i%50000 == 0:
            time_elapsed = time.time()- start
            performance_file.write(str(i)+":"+str(time_elapsed))
            cm_time += time_elapsed
            start = time.time()


    print("done")
    close_everything(consumer, performance_file)

def consume_messages_hll(consumer, pushToTopic):

    ts_min_lst = hyperloglog.HyperLogLog(0.01)
    ts_hr_lst = hyperloglog.HyperLogLog(0.01)
    time_stmp_min=0
    time_stmp_hr=0
    start = time.time()
    cm_time= time.time()
    performance_file = open("performance_file_hll.txt", "w")
    cnt_min = 0
    cnt_hr=0
    for i, message in enumerate(consumer):

        '''
            Initialise the timestamps for different durations
        '''
        if time_stmp_min==0 and time_stmp_hr==0:

            ''' Initialise for 1 minute '''
            time_stmp_min=message.value['ts']

            ''' Initialise for 10 minutes. Can change the value of miutes by changing the value of roundTo in function '''
            ## postProcessing.roundTime()
            time_stmp_hr=roundTime(dt=datetime.utcfromtimestamp(message.value['ts']), roundTo=10*60)


        '''
            Storing the messages in list for the duration of 1 minute. Then processing it for total and unique users.
        '''

        if time_stmp_min != message.value['ts'] and False:
            process_list_uids(time_stmp_min,message.value['ts'], ts_min_lst, pushToTopic, duraton='minute')
            ts_min_lst= []
            time_stmp_min= message.value['ts']

        ''' 
            Storing the messages in list for the duration of 10 minute. Then processing it for total and unique users
        '''
        message_ts_hr=roundTime(dt=datetime.utcfromtimestamp(message.value['ts']), roundTo=10*60)
        if time_stmp_hr != message_ts_hr:
            total= i-cnt_hr
            unique= len(ts_hr_lst)
            process_list_uids_hll(convert_to_unix_time(time_stmp_hr), convert_to_unix_time(message_ts_hr), total, unique ,  pushToTopic, duraton='10 minutes')
            ts_hr_lst= hyperloglog.HyperLogLog(0.01)
            time_stmp_hr= message_ts_hr

        #ts_min_lst.add(message.value['uid'])
        ts_hr_lst.add(message.value['uid'])

        if i%50000 == 0:
            time_elapsed = time.time()- start
            performance_file.write(str(i)+":"+str(time_elapsed))
            cm_time += time_elapsed
            start = time.time()


    print("done")
    close_everything(consumer, performance_file)


if __name__ == "__main__":
    consumer= create_consumer()
    pushmetric= PushMetrics()

    print('----------List processing-------')
    start = time.time()
    #consume_messages(consumer, pushmetric)
    mem_usage = memory_usage((consume_messages, (consumer, pushmetric)))
    print('Memory usage (in chunks of .1 seconds): %s' % mem_usage)
    print('Maximum memory usage: %s' % max(mem_usage))
    time_elapsed_normal = time.time() - start
    print('Time taken by list DS', time_elapsed_normal)

    print('----------HLL algorithm-------')
    consumer = create_consumer()
    start=time.time()
    mem_usage = memory_usage((consume_messages_hll, (consumer,pushmetric)))
    print('Memory usage (in chunks of .1 seconds): %s' % mem_usage)
    print('Maximum memory usage: %s' % max(mem_usage))
    #consume_messages_hll(consumer, pushmetric)
    time_elapsed_hll = time.time() - start
    print('Time taken by list HLL', time_elapsed_hll)