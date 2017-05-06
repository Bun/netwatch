
from yaml import load
from requests import get
from bs4 import BeautifulSoup


def dehtml(val):
    s = BeautifulSoup(val, 'html.parser')
    return s.text


def get_with_state(url, state, auth):
    assert not auth
    h = {}
    h['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36'
    h['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    h['Accept-Language'] = 'en-US,en;q=0.8,nl;q=0.6'
    if state.get('transport_etag'):
        h['If-None-Match'] = state['transport_etag']
    if state.get('transport_modified'):
        h['If-Modified-Since'] = state['transport_modified']
    r = get(url, headers=h)
    if 'Etag' in r.headers:
        h['transport_etag'] = r.headers['ETag']
    if 'Last-Modified' in r.headers:
        h['transport_modified'] = r.headers['Last-Modified']
    return r.text


def load_config(fname):
    return load(open(fname, encoding='utf-8'))
