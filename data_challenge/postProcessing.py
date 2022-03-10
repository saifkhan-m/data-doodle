from datetime import datetime
from datetime import timedelta

def unique_uids(messages):
    ts=set()
    for message in messages:
        ts.add(message.value['uid'])
    print(f' {len(set(ts))} unique uids')


def frames_per_duraton(time_stmp, ts):
    print(f'{time_stmp} has {len(ts)} frames')

def process_list_uids(time_stmp,lst_of_uid,  duraton='minute'):
    if  duraton=='minute':
        print(f'{time_stmp} has {len(lst_of_uid)} frames')
        frames_per_duraton(time_stmp, lst_of_uid)
        print(f' has {len(set(lst_of_uid))} unique uids')

    if  duraton=='hour':
        with open('hr.tx',"a") as f:
            f.write(f'{time_stmp} has {len(lst_of_uid)} frames\n')
            f.write( f'{time_stmp} has {len(set(lst_of_uid))} unique uids\n')


def frames_per_second_poll(ts):
    print(f' has {len(ts)} frames')

def process_raw_messages(raw_messages):
    for tp, messages in raw_messages.items():
        frames_per_second_poll(messages)
        unique_uids(messages)

def roundTime(dt=None, roundTo=60):
   """Round a datetime object to any time lapse in seconds
   dt : datetime.datetime object, default now.
   roundTo : Closest number of seconds to round to, default 1 minute.
   Author: Thierry Husson 2012 - Use it as you want but don't blame me.
   """
   if dt == None : dt = datetime.now()
   seconds = (dt.replace(tzinfo=None) - dt.min).seconds
   rounding = (seconds+roundTo/2) // roundTo * roundTo
   return dt + timedelta(0,rounding-seconds,-dt.microsecond)
