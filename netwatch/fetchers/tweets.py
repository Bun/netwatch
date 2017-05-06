#!/usr/bin/env python3
from twitter import Twitter, OAuth2
from urllib.parse import urlparse


tw = Twitter()


def get_username(url):
    # TODO
    u = urlparse(url)
    return u.path.strip('/')


def init(config):
    bt = config['twitter']['bearer-token']
    tw.auth = OAuth2(bearer_token=bt)


def fetch(state, info):
    url = info['url']
    user = get_username(url)
    data = []
    # TODO: https://dev.twitter.com/rest/reference/get/statuses/user_timeline
    # since_id
    for t in tw.statuses.user_timeline(screen_name=user, count=10):
        href = 'https://twitter.com/%s/status/%s' % (user, t['id'])
        # Unfuck URLs
        url_map = {}
        for m in t.get('extended_entities', {}).get('media', []):
            url_map[m['url']] = m.get('media_url_https') or m['url']
        text = ' '.join(url_map.get(v, v) for v in t['text'].split())
        data.append({'url': href, 'title': text})

    return data[::-1]


if __name__ == '__main__':
    from sys import argv
    from pprint import pprint
    from netwatch.utils import load_config

    if argv[1:] and argv[1:] == 'bearer-token':
        from twitter import oauth2_dance
        from os import environ
        print('Token:', oauth2_dance(environ['CONSUMER_KEY'],
                                     environ['CONSUMER_SECRET']))
        exit()

    cfg = load_config('feeds.yml')
    init(cfg)
    urls = argv[1:]
    for u in urls:
        pprint(fetch(None, {'url': u}))
