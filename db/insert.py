from neomodel import (CypherException, UniqueProperty)

from doppelgoogle.db.models import *
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

def foreach(f, it):
    for e in it:
        f(e)

class BaseNodeInserter(object):

    def __init__(self):
        self.model = type(self).model

    @staticmethod
    def update_attribute(vals):
        old_obj, new_obj, attr = vals
        old = getattr(old_obj, attr, None):
        new = getattr(new_obj, attr, None):
        if old and new:
            setattr(new_obj, attr, old)

    def update_object(self, old_obj, new_obj):
        vals = [(old_obj, new_obj, attr) for attr in self.model.update_attributes]
        foreach(self.update_attributes, vals)
        
    def save_model(obj, unique_id):
        try:
            obj.save()
        except UniqueProperty:
            existing_obj = type(obj).nodes.get(name=unique_id)
            self.update_object(obj, existing_obj)
            return self.save_model(existing_obj, unique_id)

    def create_object(self, unique_id, **kwargs):
        if not self.model.update_attributes.issuperset(set(kwargs.keys())):
            raise ValueError("Invalid arguments for update")
        obj = self.model()
        for attr, value in kwargs.items:
            setattr(obj, attr, value)
        self.save_model(obj, unique_id)

class DomainInserter(BaseNodeInserter):
    model = Domain
            

class WebPageInserter(BaseNodeInserter):
    model = WebPage

class 
            

def get_model(cls, unique_id):
    try:
        return cls.nodes.get(name=unique_id)
    except cls.DoesNotExist:
        return None

def update_webpage(webpage, urlobj):
    webpage.domain = urlobj.domain
    webpage.save()
    return webpage
    
def create_webpage(urlobj):
    webpage = 

def create_webpage(urlobj, data):
    webpage = get_model(WebPage, urlobj)
    if webpage:
        webpage = update_webpage(webpage)
    else:
        webpage = create_webpage(urlobj)

    

def insert_data(data):
    url = data['url']
    urlobj = parse_url('', url)
    
    words = data['words']
    links = data['links']

    site = create_webpage(urlobj)
    
    created_words = create_words(site, words)

    created_links = create_links(site, links)

    

    

    

    

    

    
    
    
