import json
import time
from Service import loadInfo, updateInfo
from datetime import datetime, timedelta

def is_over_30_days(time_str1, time_str2):
    time_format = '%Y-%m-%d %H:%M:%S'
    date1 = datetime.strptime(time_str1, time_format)
    date2 = datetime.strptime(time_str2, time_format)
    date_diff = abs((date2 - date1).days)
    return date_diff > 30


def recycle(name):
    info = loadInfo()
    t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    info['labels']['recycled'].append((name,t))
    for label in info['labels']:
        if label == "recycled":
            continue
        if name in info['labels'][label]:
            info['labels'][label].remove(name)
    updateInfo(info)
    return


def unrecycle(picture):
    info = loadInfo()
    recycled = info['labels']['recycled']
    for (name, past_time) in recycled:
        if name == picture:
            recycled.remove([name,past_time])
            info['labels']['no labels'].append(name)
    info['labels']['recycled'] = recycled
    updateInfo(info)
    return

def delete_click(picture):
    info = loadInfo()
    recycled = info['labels']['recycled']
    for (name, past_time) in recycled:
        if name == picture:
            recycled.remove([name,past_time])
    info['labels']['recycled'] = recycled
    updateInfo(info)
    return


def delete():
    info = loadInfo()
    recycled = info['labels']['recycled']
    t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    for (name,past_time) in recycled:
        if not is_over_30_days(past_time,t):
            recycled.remove((name,past_time))
    updateInfo(info)
    return


