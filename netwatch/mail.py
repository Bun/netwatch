from email.header import decode_header
from html import escape
#from bs4 import BeautifulSoup
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


def crazy_html(text):
    return '[omitted]'
    #durl = 'data:text/html;base64,' + b64encode(text.encode('utf8')).decode('utf8')
    #return '<iframe sandbox src="' + durl + '" width="800" height="600" seamless></iframe>'

    #b = BeautifulSoup(text, 'html.parser')
    #for tag in b.find_all():
    #    if tag.name not in ('p', 'b', 'i', 'a'):
    #        tag.name = 'span'
    #return str(b)


def render_mail(msg, fp):
    subj = _decode_header(msg['Subject'])
    print('<!DOCTYPE HTML><html><head><meta charset="utf8"><link href="m.css" rel="stylesheet" type="text/css">', file=fp)
    print('<title>', subj, '</title>', sep='', file=fp)
    print('</head><body><header>', file=fp)
    for h in ('To', 'Sender', 'From', 'CC', 'BCC', 'Subject', 'Date'):
        print_addresses(msg, h, fp)
    print('</header><section>', file=fp)
    payload = msg.get_payload()
    if not isinstance(payload, list):
        payload = [payload]
    for part in payload:
        plain = True
        if hasattr(part, 'get_content_type'):
            ct = part.get_content_type()
            print('<p><em>Content-Type:', escape(ct), '</em>', file=fp)
            if ct == 'text/html':
                text = part.get_payload(decode=True)
                plain = False
            elif ct.startswith('text/'):
                text = part.get_payload(decode=True)
            else:
                text = '[omitted]'
        else:
            text = part
        if isinstance(text, bytes):
            text = text.decode('utf8')
        if plain:
            text = '<pre class="payload">' + escape(text) + '</pre>'
        else:
            text = '<div class="payload">' + crazy_html(text) + '</div>'
        print(text, file=fp)
    print('</section></body></html>', file=fp)
