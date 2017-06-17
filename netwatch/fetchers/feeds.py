"""
Atom/RSS feed parsing
"""

import logging
import feedparser
from base64 import b64encode
from calendar import timegm

from ..utils import dehtml


feedparser.chardet = None  # broken


def init(config):
    user_agent = config.get('user-agent-extra')
    if user_agent:
        feedparser.USER_AGENT += user_agent


def _get_feed(url, mod_info, auth):
    """Obtain and parse feed, dealing with all kinds of nasty HTTP business"""
    etag, modified = mod_info
    mod = {}
    headers = None

    if auth:
        if hasattr(auth, 'encode'):
            auth = auth.encode('utf-8')
        headers = {'Authorization': b'Basic ' + b64encode(auth)}

    d = feedparser.parse(url, etag=etag, modified=modified,
                         request_headers=headers)

    if getattr(d, 'bozo', False):
        logging.warn('%s | Failure: %s', url,
                     getattr(d, 'bozo_exception', None))

    if 'status' in d:
        mod['status'] = d.status
        if d.status in (301, 302, 303):
            mod['url'] = d.href

        if d.status != 304:
            mod['etag'] = getattr(d, 'etag', None)
            mod['modified'] = getattr(d, 'modified', None)

        if (d.status < 200 or d.status > 299) and d.status not in (301, 302, 303, 304):
            logging.warn('%s | HTTP status %s', url, d.status)

    else:
        logging.warn('%s | No HTTP status?', url)
        logging.debug('%s | %s', url,
                      [(k, getattr(d, k)) for k in dir(d)])

    return d, mod


def fetch(state, info):
    url = info['url']
    auth = info.get('auth')
    entries = []
    data, mod = _get_feed(url,
                           (state.get('transport_etag'),
                            state.get('transport_modified')),
                           auth)

    if 'url' in mod:
        if mod['url'] != feed.info.url:
            # Report changed URL
            msg = u'Feed moved: {} (HTTP {})'.format(mod['url'],
                                                     mod.get('status'))
            entries.append({'id': False, 'msg': msg})

    if mod.get('etag'):
        state['transport_etag'] = mod['etag']
    if mod.get('modified'):
        state['transport_modified'] = mod['modified']

    for entry in reversed(data.entries):
        key = getattr(entry, 'guid', '') or entry.link
        if 'feedburner_origlink' in entry:
            item_url = entry.feedburner_origlink
        else:
            item_url = entry.link
        title = getattr(entry, 'title', '').strip()
        summary = dehtml(getattr(entry, 'summary', '')).strip()
        # TODO: make sure additional media is added (images)
        if title == summary:
            summary = ''
        at = timegm(entry.published_parsed)
        entries.append({'key': key,
                        'title': title,
                        'summary': summary,
                        'url': item_url,
                        'time': at})
    return entries


def feeds_fetch(info, memory):
    headers = None

    if info.auth:
        auth = info.auth
        if hasattr(auth, 'encode'):
            auth = auth.encode('utf-8')
        headers = {'Authorization': b'Basic ' + b64encode(auth)}

    d = feedparser.parse(info.url,
                         etag=memory.get('transport_etag'),
                         modified=memory.get('transport_modified'),
                         request_headers=headers)

    if getattr(d, 'bozo', False):
        logging.warn('%s | Failure: %s', info.url,
                     getattr(d, 'bozo_exception', None))

    if hasattr(d, 'status'):
        if d.status != 304:
            memory['transport_etag'] = getattr(d, 'etag', None)
            memory['transport_modified'] = getattr(d, 'modified', None)

        if (d.status < 200 or d.status > 299) and d.status not in (301, 302, 303, 304):
            logging.warn('%s | HTTP status %s', info.url, d.status)

    else:
        logging.warn('%s | No HTTP status?', info.url)

    return d


def feeds_extract(feed, memory):
    for entry in reversed(feed.entries):
        if memory_learn(memory, entry):
            continue

        if 'feedburner_origlink' in entry:
            link = entry.feedburner_origlink
        else:
            link = entry.link

        #m = r_youtube.match(link)
        #if m:
        #    link = 'http://youtu.be/' + m.group(1)

        yield {
            'summary': dehtml(entry.summary),
            'title': entry.title,
            'link': link,
        }


def feeds(info, memory):
    feed = feeds_fetch(info, memory)
    return feeds_extract(feed, memory)


availabe_fetchers = [
    ('feeds', feeds)
]
