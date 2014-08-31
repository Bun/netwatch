import logging
from datetime import datetime, timedelta
from json import load, dump

from schedule import schedule_blob


class FeedMemory(object):
    def defaults(self):
        return {
            'etag': None,
            'modified': None,
            'last_sync': None,
            'next_sync': None,
            'cached_links': {}
        }

    def __init__(self, cache_file, blob, default_target):
        self.cache_file = cache_file
        self.blob = blob
        self.url = blob['url']
        self.prefix = blob['prefix']
        self.target = blob.get('target', default_target)
        self.auth = blob.get('auth')
        self.last_sync = None
        self.next_sync = None
        self._load()

    def _load(self):
        try:
            fp = open(self.cache_file)
        except IOError as e:
            if e.errno != 2:
                raise
            fp = None

        data = self.defaults()
        only_defaults = True

        if fp:
            try:
                v = load(fp)
            except ValueError:
                v = None

            if isinstance(v, dict):
                only_defaults = False
                data.update(v)

        if only_defaults:
            logging.warn('Loaded feed defaults for %s', self.url)

        for k, v in data.items():
            setattr(self, k, v)

    def save(self):
        try:
            expire = (datetime.now() - timedelta(days=128)).timestamp()
            cached_links = {k: v for k, v in self.cached_links.items() if v > expire}
            self.cached_links = cached_links
        except:
            logging.exception('Goofed')

        fp = open(self.cache_file, 'w')

        dump({
            'url': self.url,
            'etag': self.etag,
            'modified': self.modified,
            'last_sync': self.last_sync,
            'next_sync': self.next_sync,
            'cached_links': self.cached_links
        }, fp)

    def synced(self):
        now = datetime.now()
        sync = schedule_blob(self.blob, now)
        #logging.debug('%s | Sync at: %s', self.url, sync)
        self.last_sync = now.timestamp()
        self.next_sync = sync.timestamp()

    def learn(self, entry):
        now = datetime.now()
        ret = self.knows(entry)
        key = getattr(entry, 'guid', '') or entry.link
        self.cached_links[key] = now.timestamp()
        return ret

    def knows(self, entry):
        key = getattr(entry, 'guid', '') or entry.link
        return key in self.cached_links


# -----------------------------------------------------------------------------


class FeedStatus(object):
    def defaults(self):
        return {
            'etag': None,
            'modified': None,
            'last_sync': None,
            'next_sync': None,
            'cached_links': {}
        }

    def __init__(self, cache_file, url):
        self.cache_file = cache_file
        self.url = url
        self.last_sync = None
        self.next_sync = None
        self._load()

    def schedule(self, at):
        logging.debug('%s | Schedule: %s', self.url, at)
        self.next_sync = at

    def learn(self, entry):
        now = datetime.now()
        ret = self.knows(entry)
        self.cached_links[entry.link] = now.timestamp()
        logging.debug('%s | learn %s', self.url, entry.link)
        return ret

    def knows(self, entry):
        return entry.link in self.cached_links


    def fetched(self, etag, modified):
        now = datetime.now()
        self.last_sync = now.timestamp()
        self.etag = etag
        self.modified = modified


    # -- I/O ------------------------------------------------------------------

    def _load(self):
        try:
            fp = open(self.cache_file)
        except IOError as e:
            if e.errno != 2:
                raise
            fp = None

        data = self.defaults()
        only_defaults = True

        if fp:
            try:
                v = load(fp)
            except ValueError:
                v = None

            if isinstance(v, dict):
                only_defaults = False
                data.update(v)

        if only_defaults:
            logging.warn('Loaded feed defaults for %s', self.url)

        for k, v in data.items():
            setattr(self, k, v)

    def save(self):
        try:
            expire = (datetime.now() - timedelta(days=128)).timestamp()
            cached_links = {k: v for k, v in self.cached_links.items() if v > expire}
            self.cached_links = cached_links
        except:
            logging.exception('Goofed')

        with open(self.cache_file, 'w') as fp:
            dump({
                'url': self.url,
                'etag': self.etag,
                'modified': self.modified,
                'last_sync': self.last_sync,
                'next_sync': self.next_sync,
                'cached_links': self.cached_links
            }, fp)
