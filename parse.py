"""
"""
from datetime import datetime

import logging
import feedparser
from base64 import b64encode

feedparser.USER_AGENT += ' +https://nx3d.org/contact'


def feed_parse(feed):
    now = datetime.now().timestamp()

    if feed.next_sync is not None and now < feed.next_sync:
        #logging.debug('%s | In %d', feed.url, feed.next_sync - now)
        return

    logging.debug('%s | Fetch', feed.url)

    headers = None

    if feed.auth:
        auth = feed.auth
        if hasattr(auth, 'encode'):
            auth = auth.encode('utf-8')
        headers = {'Authorization': b'Basic ' + b64encode(auth)}

    d = feedparser.parse(feed.url,
                         etag=feed.etag,
                         modified=feed.modified,
                         request_headers=headers)

    if getattr(d, 'bozo', False):
        logging.warn('%s | Failure: %s', feed.url,
                     getattr(d, 'bozo_exception', None))

    if hasattr(d, 'status'):
        if d.status != 304:
            feed.etag = getattr(d, 'etag', None)
            feed.modified = getattr(d, 'modified', None)

            if d.status < 200 or d.status > 299:
                logging.debug('%s | status=%r etag=%r modified=%r', feed.url,
                              d.status, feed.etag, feed.modified)

        if (d.status < 200 or d.status > 299) and d.status != 304:
            logging.warn('%s | HTTP status %s', feed.url, d.status)
        else:
            feed.synced()

    else:
        logging.warn('%s | No HTTP status?', feed.url)

    return d


'''
if __name__ == '__main__' and False:
    from yaml import load as yaml_load

    logging.basicConfig(level=logging.DEBUG,
                        format='[%(asctime)s] %(levelname)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    def cb(blob, status, entries):
        for e in entries:
            logging.info('>> %s >> %s (%s)', blob['prefix'], e.title, e.link)

    config = yaml_load(open('feeds.yml'))
    fetch_feeds(config['feeds'], cb)
'''
