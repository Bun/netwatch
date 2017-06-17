from time import time
from json import load, dump
from datetime import timedelta

CACHE_MIN_SIZE = 64
CACHE_MAX_TIME = timedelta(days=31).total_seconds()


def memory_load(fname):
    try:
        fp = open(fname)
    except IOError as e:
        if e.errno != 2:
            raise
        return {'history': {}}

    data = load(fp)

    # Migrate old data
    if 'next_sync' in data:
        data = {
            'schedule_last_sync': data.get('last_sync'),
            'schedule_next_sync': data.get('next_sync'),
            'transport_etag': data.get('etag'),
            'transport_modified': data.get('modified'),
            'history': data.get('cached_links'),
        }

    data.setdefault('history', {})
    return data


def memory_save(fname, memory):
    history = memory.get('history', {})
    if len(history) > CACHE_MIN_SIZE:
        expire = time() - CACHE_MAX_TIME
        def expired(v):
            t = v['fetched'] if isinstance(v, dict) else v
            return t > expire
        memory['history'] = {k: v for k, v in history.items() if expired(v)}
    with open(fname, 'w') as fp:
        dump(memory, fp, indent=True)


def memory_learn(mem, key, entry_time=None):
    ret = key in mem['history']
    v = {'fetched': int(time())}
    if entry_time is not None:
        v['entry'] = entry_time
    mem['history'][key] = v
    return ret
