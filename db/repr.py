

__all__ = ['WebPageRepr', 'WordRepr', 'DomainRepr', 'SubdomainRepr', 'TLDRepr', 'LinkRepr']

import datetime

class BaseRepr(object):
    time = False

    def __init__(self, **kwargs):
        self.dct = kwargs.copy()
        if self.time:
            self.dct['time'] = str(datetime.datetime.now())

    @property
    def name(self):
        return self.dct['name']

    def __str__(self):
        pieces = []
        for key, value in self.dct.items():
            if isinstance(value, str):
                pieces.append('{0}: "{1}"'.format(key, value))
            else:
                pieces.append('{0}: {1}'.format(key, value))
        return "{{{0}}}".format(", ".join(pieces))


class WebPageRepr(BaseRepr):
    time = True
    label = 'WebPage'

class WordRepr(BaseRepr):
    label = 'Word'

class DomainRepr(BaseRepr):
    label = 'Domain'

class SubdomainRepr(BaseRepr):
    label = 'Subdomain'

class TLDRepr(BaseRepr):
    label = 'TLD'

class LinkRepr(BaseRepr):
    label = 'Link'
