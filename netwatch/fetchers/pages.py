from requests import get
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import logging


def fetch(state, info):
    url = info['url']
    etag = state.get('transport_etag')
    modified = state.get('transport_modified')
    headers = {}
    if etag is not None:
        headers['If-None-Match'] = etag
    if modified is not None:
        headers['If-Modified-Since'] = modified

    r = get(url, headers=headers)
    if r.status_code < 200 or r.status_code > 299:
        logging.info('%s | Fetch failed with status %s', url, r.status_code)
        return []

    state['transport_etag'] = r.headers.get('etag')
    state['transport_modified'] = r.headers.get('last-modified')

    doc = BeautifulSoup(r.text, 'html.parser')
    limit = info.get('patterns', [])
    kind = info.get('kind', 'urls')
    if kind == 'images':
        for img in doc.find_all('img'):
            href = img.get('src') or ''
            if not href:
                continue
            href = urljoin(url, href)
            logging.info('images %s', href)
            if limit and not any(p in href for p in limit):
                continue
            alt = str(img.get('alt', ''))
            title = str(img.get('title', ''))
            yield {'url': href, 'title': alt, 'summary': title}
    else:
        for a in doc.find_all('a'):
            href = a.get('href') or ''
            if not href:
                continue
            href = urljoin(url, href)
            if limit and not any(p in href for p in limit):
                continue
            # TODO: optionally get parent element text if parent
            text = str(a.text)
            text = text[:1].upper() + text[1:]
            yield {'url': href, 'title': text}
