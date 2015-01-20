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


def get_webpage(url):
    try:
        return WebPage.nodes.get(url=url)
    except WebPage.DoesNotExist:
        return None

def create_webpage_and_domain(url, ):
    webpage = get_webpage(url)
    if webpage:
        webpage = update_webpage(urL)
    else:
        webpage = create_webpage(url)

    

def insert_data(data):
    url = data['url']
    urlobj = parse_url('', url)
    
    words = data['words']
    links = data['links']

    site = create_webpage_and_domain(url)
    
    created_words = create_words(site, words)

    created_links = create_links(site, links)

    

    

    

    

    

    
    
    
