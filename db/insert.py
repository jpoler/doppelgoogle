from neomodel import (CypherException, UniqueProperty)

from doppelgoogle.db.models import (Link, WordUsed, Domain, Subdomain,
                                    Subdomain, TopLevelDomain, WebPage, Word)
# from doppelgoogle.url_utils.url import parse_url

# I am going to attempt to write this top down for one main reason:
# if I write my functions to be general enough, then I can originally just use
# direct database queries to see if nodes are already in the database
# if this method is too slow then I can optimize with in-memory data structures
# I am going to start with just database queries to keep things simple, and
# then I'll check performance with cProfile

class EntryExists(Exception):
    pass

class InsertionFailed(Exception):
    pass

    
class BaseNodeInterface(object):

    @staticmethod
    def save_node(node):
        node.save()

    @classmethod
    def get_node(cls, unique_id):
        try:
            return cls.model.nodes.get(name=unique_id)
        except cls.model.DoesNotExist as e:
            return cls.model(name=unique_id)

    @classmethod
    def update_node(cls, node, **kwargs):
        node.__dict__.update(kwargs)
        

    @classmethod
    def create_or_update_object(cls, name=None, **kwargs):
        if not name:
            raise ValueError("name is a required argument")
        if not cls.model.update_attributes.issuperset(set(kwargs.keys())):
            raise ValueError("Invalid arguments for update")

        node = cls.get_node(name)
        cls.update_node(node)
        cls.save_node(node)
        return node

    

class DomainInterface(BaseNodeInterface):
    model = Domain

class WebPageInterface(BaseNodeInterface):
    model = WebPage

class SubdomainInterface(BaseNodeInterface):
    model = Subdomain

class TopLevelDomainInterface(BaseNodeInterface):
    model = TopLevelDomain

class WebPageInterface(BaseNodeInterface):
    model = WebPage

class BaseRelationInterface(object):
    pass


class 


def insert_data(data):
    url = data['url']
    urlobj = parse_url('', url)
    
    words = data['words']
    links = data['links']

    site = create_webpage(urlobj)
    
    created_words = create_words(site, words)

    created_links = create_links(site, links)

    


    

    

    

    
    
    
