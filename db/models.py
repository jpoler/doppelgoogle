from neomodel import (StructuredNode, StringProperty, IntegerProperty, DateTimeProperty,
                      RelationshipTo, RelationshipFrom, StructuredRel, cardinality)

from uuid import uuid4
import datetime

class Link(StructuredRel):
    href = StringProperty()
    rel = StringProperty(default="")
    target = StringProperty(default="")

class Domain(StructuredNode):
    name = StringProperty(unique_index=True, required=True)
    pages = RelationshipTo('WebPage', 'DOMAIN_CONTAINS_PAGE', cardinality=cardinality.ZeroOrMore)

class WebPage(StructuredNode):
    url = StringProperty(unique_index=True, required=True)
    visited = DateTimeProperty(default=lambda: datetime.datetime.now())

    domain = RelationshipFrom('Domain', 'WEBPAGE_WITHIN_DOMAIN', cardinality=cardinality.One)
    words = RelationshipTo('Word', 'PAGE_CONTAINS_WORD', cardinality=cardinality.ZeroOrMore)
    links = RelationshipTo('WebPage', 'LINKS_TO', cardinality=cardinality.ZeroOrMore)

class Word(StructuredNode):
    name = StringProperty(unique_index=True, required=True)
    webpages = RelationshipFrom('WebPage', 'WORD_WITHIN_WEBPAGE', cardinality=cardinality.ZeroOrMore)

