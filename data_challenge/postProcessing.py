from datetime import datetime
from datetime import timedelta
import time
def createJson(duration, startTime, endTime, totalUIDs, uniqueUIDs):

    jsonDict = {
        "duration": duration,
        "Start_time": startTime,
        "End_time": endTime,
        "Metric": {
            "total_UIDs": totalUIDs,
            "unique_UIDs": uniqueUIDs
        }
    }
    return jsonDict
def convert_to_unix_time(timestmp):
    return int(time.mktime(timestmp.timetuple()))

def process_list_uids(time_stmp_strt, time_stmp_end, lst_of_uid, pushToTopic,  duraton='minute'):
    totalUIDs = len(lst_of_uid)
    uniqueUIDs = len(set(lst_of_uid))
    msgJSON =createJson(duraton, time_stmp_strt, time_stmp_end, totalUIDs, uniqueUIDs)
    #print(msgJSON)
    pushToTopic.push(msgJSON)




def roundTime(dt=None, roundTo=60):
   """Round a datetime object to any time lapse in seconds
   dt : datetime.datetime object, default now.
   roundTo : Closest number of seconds to round to, default 1 minute.
   Author: Thierry Husson 2012
   """
   if dt == None : dt = datetime.now()
   seconds = (dt.replace(tzinfo=None) - dt.min).seconds
   rounding = (seconds+roundTo/2) // roundTo * roundTo
   return dt + timedelta(0,rounding-seconds,-dt.microsecond)


"""
    if  duraton=='hour':
        with open('hr.tx',"a") as f:
            f.write(f'{time_stmp_strt} has {len(lst_of_uid)} frames\n')
            f.write( f'{time_stmp_strt} has {len(set(lst_of_uid))} unique uids\n')

def frames_per_second_poll(ts):
    print(f' has {len(ts)} frames')

def unique_uids(messages):
    ts=set()
    for message in messages:
        ts.add(message.value['uid'])
    print(f' {len(set(ts))} unique uids')

"""