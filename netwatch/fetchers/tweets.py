#!/usr/bin/env python3
from twitter import Twitter, OAuth2
from urllib.parse import urlparse
from time import strptime
from calendar import timegm
from pprint import pprint

tw = Twitter()


def get_username(url):
    # TODO
    u = urlparse(url)
    return u.path.strip('/')


def init(config):
    bt = config['twitter']['bearer-token']
    tw.auth = OAuth2(bearer_token=bt)


def _parse_time(v):
    return timegm(strptime(v, '%a %b %d %H:%M:%S +0000 %Y'))


def fetch(state, info, verbose=False):
    conf = info.get('conf', {})
    require_media = conf.get('media') is True
    exclude_replies = conf.get('reply') is False

    url = info['url']
    user = get_username(url)
    data = []
    kwargs = {}
    if state.get('tw_latest_id'):
        kwargs['since_id'] = state['tw_latest_id']

    # TODO: https://dev.twitter.com/rest/reference/get/statuses/user_timeline
    # include_rts
    latest_id = None
    for t in tw.statuses.user_timeline(screen_name=user, count=32, trim_user=1,
                                       exclude_replies=exclude_replies,
                                       tweet_mode='extended', **kwargs):
        if verbose:
            pprint(t)
        post_id = t['id']
        if latest_id is None or post_id > latest_id:
            latest_id = post_id
        href = 'https://twitter.com/%s/status/%s' % (user, t['id'])
        # Unfuck URLs
        url_map = {}
        for m in t.get('extended_entities', {}).get('media', []):
            url_map[m['url']] = m.get('media_url_https') or m['url']
        for m in t.get('entities', {}).get('urls', []):
            url_map[m['url']] = m.get('expanded_url') or m['url']
        if require_media and not url_map:
            # TODO
            pass
        text = ' '.join(url_map.get(v, v) for v in t['full_text'].split())
        at = _parse_time(t['created_at'])
        data.append({'url': href,
                     'title': text,
                     'time': at})
    if latest_id is not None:
        state['tw_latest_id'] = latest_id
    return data[::-1]


if __name__ == '__main__':
    from sys import argv
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
        blob = {'url': u}
        for v in cfg.get('tweets', []):
            if get_username(v['url']).lower() == u.lower():
                blob = v
                break

        pprint(fetch({}, blob, True))
