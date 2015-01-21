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

def create_webpage_and_domain(urlobj, data):
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

    

    

    

    

    

    
    
    
