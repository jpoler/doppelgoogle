# set([u'rel', u'text', u'accesskey', u'hreflang', u'href', u'id', u'lang', u'style', u'target', u'title', u'class', u'onclick', u'action', u'data-converttitle-hans', u'type', u'dir', u'tabindex'])

__all__ = ['Link', 'WordUsed', 'Domain', 'WebPage', 'Word']

from neomodel import (StructuredNode, StringProperty, IntegerProperty, DateTimeProperty,
                      RelationshipTo, RelationshipFrom, StructuredRel, cardinality,
                      ArrayProperty)

from uuid import uuid4
import datetime



class Link(StructuredRel):
    _href = StringProperty()
    _link_rel = StringProperty()
    _target = StringProperty()
    _text = StringProperty()
    _accesskey = StringProperty()
    _hreflang = StringProperty()
    _id = StringProperty()
    _lang = StringProperty()
    _style = StringProperty()
    _title = StringProperty()
    _class = StringProperty()
    _onclick = StringProperty()
    _action = StringProperty()
    _type = StringProperty()
    _dir = StringProperty()
    _tabindex = StringProperty()
    
class WordUsed(StructuredRel):
    freq = IntegerProperty(required=True)
    locations = ArrayProperty(required=True)

class Domain(StructuredNode):
    name = StringProperty(unique_index=True, required=True)

    subdomain = RelationshipTo('Subdomain', 'DOMAIN_CONTAINS_SUBDOMAIN', cardinality=cardinality.OneOrMore)
    tld = RelationshipTo('TopLevelDomain', 'TLD_CONTAINS_DOMAIN', cardinality=cardinality.OneOrMore)
    pages = RelationshipTo('WebPage', 'DOMAIN_CONTAINS_WEBPAGE', cardinality=cardinality.OneOrMore)

class Subdomain(StructuredNode):
    name = StringProperty(unique_index=True, required=True)

    domain = RelationshipFrom('Domain', 'DOMAIN_CONTAINS_SUBDOMAIN', cardinality=cardinality.OneOrMore)

class TopLevelDomain(StructuredNode):
    name = StringProperty(unique_index=True, required=False)

    domain = RelationshipFrom('Domain', 'TLD_CONTAINS_DOMAIN', cardinality=cardinality.OneOrMore)
    

class WebPage(StructuredNode):
    url = StringProperty(unique_index=True, required=True)
    visited = DateTimeProperty(default=lambda: datetime.datetime.now())
    encoding = StringProperty()

    domain = RelationshipFrom('Domain', 'DOMAIN_CONTAINS_WEBPAGE', cardinality=cardinality.One)
    words = RelationshipTo('Word', 'PAGE_CONTAINS_WORD',
                           cardinality=cardinality.ZeroOrMore, model=WordUsed)
    links_to = RelationshipTo('WebPage', 'LINKS_TO',
                              cardinality=cardinality.ZeroOrMore, model=Link)
    links_from = RelationshipFrom('WebPage', 'LINKS_TO',
                                  cardinality=cardinality.ZeroOrMore, model=Link)

class Word(StructuredNode):
    name = StringProperty(unique_index=True, required=True)
    webpages = RelationshipFrom('WebPage', 'PAGE_CONTAINS_WORD',
                                cardinality=cardinality.ZeroOrMore, model=WordUsed)

