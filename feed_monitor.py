#!/usr/bin/env python3
# coding: utf-8

import re
import logging
from time import sleep #, strftime
from os import rename
from os.path import exists

from parse import feed_parse
from memory import FeedMemory
from srpc import Client


def feed_formatter(memory, feed, formatter):
    new_entries = []

    for entry in reversed(feed.entries):
        if memory.learn(entry):
            continue

        new_entries.append(formatter(memory, entry))

    return new_entries


# --- IRC formatter -----------------------------------------------------------

URL_COLOR = 14
r_youtube = re.compile(r'^https?://(?:www\.)?youtube\.com/watch\?v=([^&]*)(?:&.*)?$')


def limit(datum, length=256):
    if len(datum) > length:
        return datum[:length - 1] + u'…'

    return datum


def sane(datum):
    return re.sub(r'[\x00-\x20]+', ' ', datum)


def default_formatter(fm, entry):
    title = limit(sane(entry.title))

    if 'feedburner_origlink' in entry:
        link = sane(entry.feedburner_origlink)
    else:
        link = sane(entry.link)

    m = r_youtube.match(link)

    if m:
        link = 'http://youtu.be/' + m.group(1)

    #try:
    #    t = lambda v: v and strftime('%a, %d %b %Y %H:%M:%S', v)
    #    pparsed = getattr(entry, 'published_parsed', None)
    #    uparsed = getattr(entry, 'updated_parsed', None)
    #    logging.debug('%s | published: %s', link, t(pparsed))
    #    logging.debug('%s | updated:   %s', link, t(uparsed))
    #except:
    #    logging.exception('default_formatter')

    return u'\x02{}\x02 » {} \x03{}{}'.format(fm.prefix, title, URL_COLOR,
                                              link)

# ------------------------------------------------------------------------------

def _fetch_feed(memory, formatter, outq):
    feed = feed_parse(memory)

    if not feed:
        return

    if hasattr(feed, 'status'):
        if feed.status in (301, 302, 303):
            # Report changed URL
            msg = u'\x02{}\x02 » Feed moved: {} (HTTP {})'.format(memory.prefix, feed.href, feed.status)
            outq.add({'msg': msg, 'target': memory.target})

        elif (feed.status < 200 or feed.status > 299) and feed.status != 304 and feed.status != 503:
            # Report status
            msg = u'\x02{}\x02 » Error {}'.format(memory.prefix, feed.status)
            outq.add({'msg': msg, 'target': memory.target})

    new_entries = feed_formatter(memory, feed, formatter)
    N = 10

    # Show last N entries
    for entry in new_entries[-N:]:
        outq.add({'msg': entry, 'target': memory.target})

    if len(new_entries) > N:
        # XXX if this type of message ends up getting queued more than
        # once, the results will be weird for the end-user
        e = {'msg': u'\x02{}\x02 » {} more: {}'.format(memory.prefix,
                                                       len(new_entries) - N,
                                                       feed['feed']['link']),
             'target': memory.target}
        outq.add(e)

    memory.save()


def fetch_feeds(feeds, outq):
    # Fetch new entries
    for memory, formatter in feeds:
        try:
            _fetch_feed(memory, formatter, outq)
        except:
            logging.exception('%s | Error while fetching feed:', memory.url)

'''
def _feed_url_encoded(url):
    return sha1(url.encode('utf8')).hexdigest()

def fetch_feeds(blobs, callback, cache_path='.fc'):
    now_dt = datetime.now()
    now = now_dt.timestamp()

    for blob in blobs:
        url = blob['url']
        cache_file = join(cache_path, _feed_url_encoded(url))

        status = FeedStatus(cache_file, url)

        if 'x' in status.url:
            pass
        elif status.next_sync is not None and now < status.next_sync:
            logging.debug('%s | No sync (%d)', status.url,
                          status.next_sync - now)
            continue

        entries = list(_fetch_feed(status))

        if entries:
            callback(blob, status, entries)

        status.schedule(schedule_blob(blob, now_dt))

        #status.save()
'''


# ---- Output -----------------------------------------------------------------

def spam_queue(q, socket):
    """ Spam the queue over RPC """
    if q.empty():
        return

    rpc = Client(socket)
    sleep_time = 0.1

    while not q.empty():
        msg = q.peek()
        # TODO: confirmation
        rpc.send(msg)
        q.get()
        sleep(sleep_time)
        sleep_time = min(1.5, sleep_time * 2)

# -----------------------------------------------------------------------------

def _cache_file(feed):
    old_cache_file = '.fc/' + sha1(feed['url'].encode('utf8')).hexdigest()

    # TODO: will break if cache file is reused
    name = feed['url']

    if feed.get('name'):
        name = feed['name']
    elif feed.get('prefix'):
        name = feed['prefix']

    name = re.sub(r'[^a-zA-Z0-9_]+', '-', name)
    name = name.strip('-').lower()
    cache_file = '.fc/' + name

    if exists(old_cache_file) and not exists(cache_file):
        logging.debug('%s -> %s', old_cache_file, cache_file)
        rename(old_cache_file, cache_file)

    return cache_file


# -----------------------------------------------------------------------------


if __name__ == '__main__':
    from fqueue import FQueue
    from hashlib import sha1
    from yaml import load
    from io import open
    from socket import setdefaulttimeout

    setdefaulttimeout(20)

    logging.basicConfig(level=logging.DEBUG,
        format='[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')

    config = load(open('feeds.yml', encoding='utf-8'))
    feeds = []

    for feed in config['feeds']:
        cache_file = _cache_file(feed)
        feeds.append((FeedMemory(cache_file, feed, config['target']),
                      default_formatter))

    q = FQueue('.fc/queue')

    try:
        fetch_feeds(feeds, q)
        spam_queue(q, config['rpc'])

    finally:
        q.save()
