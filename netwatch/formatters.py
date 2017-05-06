import re


def _limit(datum, length=256):
    if len(datum) > length:
        return datum[:length - 1] + u'…'

    return datum


def _sane(datum):
    return re.sub(r'[\x00-\x20]+', ' ', datum)


def default_formatter(fm, entry):
    title = _limit(_sane(entry.title))

    # {{{ filters
    if 'feedburner_origlink' in entry:
        link = _sane(entry.feedburner_origlink)
    else:
        link = _sane(entry.link)

    m = r_youtube.match(link)

    if m:
        link = 'http://youtu.be/' + m.group(1)
    # }}}

    # {{{ debug
    try:
        t = lambda v: v and strftime('%a, %d %b %Y %H:%M:%S', v)
        pparsed = getattr(entry, 'published_parsed', None)
        uparsed = getattr(entry, 'updated_parsed', None)
        logging.debug('%s | published: %s', link, t(pparsed))
        logging.debug('%s | updated:   %s', link, t(uparsed))
    except:
        logging.exception('default_formatter')
    # }}}

    return u'\x02{}\x02 » {} \x03{}{}'.format(blob['prefix'], title, URL_COLOR,
                                              link)

def irc_format_many(blob, feed, entries):
    return u'\x02{}\x02 » {} new entries: {}'.format(blob['prefix'],
                                                     len(entries),
                                                     feed['feed']['link'])

def irc_format_single(blob, feed, entry):
    pass

