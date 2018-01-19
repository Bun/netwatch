from email.header import decode_header
from html import escape
from bs4 import BeautifulSoup
#from base64 import b64encode


def _decode_header(v):
    ret = ''
    for part in decode_header(v):
        if isinstance(part[0], str):
            ret += part[0]
        else:
            ret += part[0].decode(part[1])
    return ret


def print_addresses(msg, k, fp):
    if msg[k] is None: return
    v = _decode_header(msg[k])
    print('''<div class="hdrs">
        <span class="hdr-k">%s</span>
        <span class="hdr-v">%s</span>
</div>''' % (escape(k), escape(v)),
          file=fp)


WHITELIST = {'p', 'i', 'b', 'a', 'span',
             'div', 'ul', 'li', 'hr',
             'br', 'img', 'font',
             'strong', 'em',
             'table', 'tr', 'td'}
# src style
WHITELIST_ATTR = {'bgcolor', 'border', 'cellpadding', 'cellspacing',
                  'alt', 'width', 'height', 'size', 'type',
                  'href', 'color', 'align', 'valign',
                  'src',
                  'noshade'}

def only_urls(v):
    if v.startswith('http:') or v.startswith('https:'):
        return v
    return ''


def crazy_html(text):
    #return '[omitted]'
    #durl = 'data:text/html;base64,' + b64encode(text.encode('utf8')).decode('utf8')
    #return '<iframe sandbox src="' + durl + '" width="800" height="600" seamless></iframe>'
    replaced = set()
    b = BeautifulSoup(text, 'html.parser')
    body = b.find('body')
    if body:
        b = body
        b.name = 'div'
        b.attrs = {}
    for tag in b.find_all():
        otag = tag.name
        if tag.name in ('style', 'script'):
            tag.extract()
        elif tag.name not in WHITELIST:
            if tag.name not in replaced:
                replaced.add(tag.name)
            tag.name = 'span'
        if tag.attrs:
            a = {}
            for k, v in tag.attrs.items():
                if k in ('href', 'src'):
                    v = only_urls(v)
                if k in WHITELIST_ATTR:
                    a[k] = v
                    continue
                n = otag + '.' + k
                if n not in replaced:
                    replaced.add(n)
            if otag in ('a', 'img'):
                a['referrerpolicy'] = 'no-referrer'
            tag.attrs = a
    trailer = ', '.join(replaced)
    if trailer:
        trailer = '<!-- ' + trailer + ' -->'
    return str(b) + trailer

MULTIPART_ACCEPTABLE = {'multipart/signed',
                        'multipart/mixed',
                        'multipart/alternative'}

def recursive_collect_text(msg):
    def _decode(text):
        if isinstance(text, bytes):
            return text.decode('utf8')
        return text

    def _rendered(ct, part, payload):
        html = plaintext = ''
        if ct in MULTIPART_ACCEPTABLE:
            return recursive_collect_text(part)
        elif ct == 'text/html':
            html = payload
        elif ct.startswith('text/'):
            plaintext = payload
        else:
            plaintext = '[omitted ' + ct + ']'
        if plaintext:
            plaintext = '<pre class="payload">' + escape(plaintext) + '</pre>'
        if html:
            html = '<div class="payload">' + crazy_html(html) + '</div>'
        return html, plaintext

    ct = msg.get_content_type()
    if ct in MULTIPART_ACCEPTABLE:
        parts = msg.get_payload()
        if not isinstance(parts, list):
            return '', '<pre class="payload">[invalid ' + escape(ct) + ' ignored]</pre>'
        html = plaintext = ''
        for part in parts:
            ct = part.get_content_type()
            r = _rendered(ct, part, _decode(part.get_payload(decode=True)))
            html += r[0]
            plaintext += r[1]
        return html, plaintext
    return _rendered(ct, msg, _decode(msg.get_payload(decode=True)))


def render_mail(msg, fp):
    subj = _decode_header(msg['Subject'])
    print('<!DOCTYPE HTML><html><head><meta charset="utf8"><link href="m.css" rel="stylesheet" type="text/css">', file=fp)
    print('<title>', subj, '</title>', sep='', file=fp)
    print('</head><body><header>', file=fp)
    for h in ('To', 'Sender', 'From', 'CC', 'BCC', 'Subject', 'Date'):
        print_addresses(msg, h, fp)
    print('</header><section>', file=fp)
    html, plaintext = recursive_collect_text(msg)
    if html:
        print(html, file=fp)
    else:
        print(plaintext, file=fp)
    print('</section></body></html>', file=fp)
