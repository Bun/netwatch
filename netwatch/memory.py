from time import time
from json import load, dump


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
    fp = open(fname, 'w')
    dump(memory, fp)


def memory_learn(mem, key):
    ret = key in mem['history']
    mem['history'][key] = time()
    return ret
