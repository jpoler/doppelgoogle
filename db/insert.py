from neomodel import (CypherException, UniqueProperty)
from neomodel.relationship_manager import RelationshipDefinition

from doppelgoogle.db.models import (Link, WordUsed, Domain, Subdomain,
                                    Subdomain, TopLevelDomain, WebPage, Word)
# from doppelgoogle.url_utils.url import parse_url
from doppelgoogle.crawler.crawl import URLParser, get_parsed_url
from doppelgoogle.exceptions.exceptions import URLParseException, InvalidUniqueKeyException

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
    def get_object(cls, name=None, **kwargs):
        if not name:
            raise InvalidUniqueKeyException("name is a required argument")
        if not cls.model.update_attributes.issuperset(set(kwargs.keys())):
            raise ValueError("Invalid arguments for update")

        node = cls.get_node(name)
        cls.update_node(node)
        cls.save_node(node)
        return node

    

class DomainInterface(BaseNodeInterface):
    model = Domain

class SubdomainInterface(BaseNodeInterface):
    model = Subdomain

class TopLevelDomainInterface(BaseNodeInterface):
    model = TopLevelDomain

class WebPageInterface(BaseNodeInterface):
    model = WebPage



class WordInterface(BaseNodeInterface):
    model = Word

## change the words dictionary to contain a dictionary with freq and locations as keys if not already


## mapping of relations objects to their relations

class BaseConnector(object):

    @staticmethod
    def check_prop(prop, target):
        if isinstance(prop, RelationshipDefinition):
            return (isinstance(target, prop.definition['node_class']) and prop.definition['direction'] == 1)
        return False

    @staticmethod
    def check_relation_properties(relation, kwargs):
        model = relation.definition['model']
        if not model:
            return not kwargs
        keys_set = set(kwargs.keys())
        return model.valid_properties.issuperset(keys_set)
            

    @classmethod
    def connect_objects(cls, source, target, **kwargs):
        for name, prop in source.defined_properties().iteritems():
        # print("BaseConnector connect_objects()")

            if cls.check_prop(prop, target):
                # now check to make sure all of the properties are in the relationship definition
                if cls.check_relation_properties(prop, kwargs):
                    result = source.__dict__[name].connect(target, kwargs)
                    source.save()
                    target.save()
        return False

connect_objects = BaseConnector.connect_objects
            
class PageInserter(object):

    def __init__(self, urlobj):
        # print("PageInserter __init__()")
        self.urlobj = urlobj
        self.url = urlobj.url.geturl()
        self.page = WebPageInterface.get_object(name=self.url)
        self.subdomain = SubdomainInterface.get_object(name=self.urlobj.subdomain)
        self.domain = DomainInterface.get_object(name=self.urlobj.domain)
        self.tld = TopLevelDomainInterface.get_object(name=self.urlobj.tld)
        self.make_connections()

    def make_connections(self):
        # print("make connections connecting page")
        connect_objects(self.domain, self.page)
        connect_objects(self.domain, self.subdomain)
        connect_objects(self.domain, self.tld)
        self.save_objects()

    def save_objects(self):
        self.page.save()
        self.subdomain.save()
        self.domain.save()
        self.tld.save()


    
class WordInserter(object):
    model = Word

    @classmethod
    def create_word(cls, word):
        if isinstance(word, str):
            word = unicode(word)
                
        clean = filter(unicode.isalpha, word.lower())
        return WordInterface.get_object(name=clean)

    @classmethod
    def insert_words(cls, words, page):
        # print("WordInserter insert_words()")
        for word, dct in words.iteritems():
            try:
                wordobj = cls.create_word(word)
                # print("Connecting a word to a page: {}".format(word))
                connect_objects(page, wordobj, **dct)

            except (UnicodeError, InvalidUniqueKeyException):
                continue
        
    
        
        
class LinkInserter(object):

    @staticmethod
    def fix_attr_names(attrs):
        result = {}

        for name, value in attrs.iteritems():
            result['_' + name] = value
        return result

    @classmethod
    def create_link(cls, link_page, attrs, page):
        fixed_attrs = cls.fix_attr_names(attrs)
        # print("connecting page to a link: {}".format(link_page.page))
        print(page, link_page)
        connect_objects(page, link_page, **fixed_attrs)
        page.save()
        link_page.save()

    @classmethod
    def insert_links(cls, links, page):
        # print("LinkInserter insert_links()")
        links_copy = links.copy()
        for link, attrs in links_copy.iteritems():
            try:
                urlobj = URLParser(page.name, link)
                link_page = PageInserter(urlobj)
                cls.create_link(link_page.page, attrs,  page)
            except URLParseException:
                del links[link]
        
                
            
    

# This class is not catching the exception raised by URLParser on purpose
#if url is bad, it is responsibility of instantiater to handle error
class DataInserter(object):

    def __init__(self, data):
        # print("DataInserter __init__")
        self.data = data
        self.url = data['url']
        self.words = data['words']
        self.links = data['links']
        self.urlobj = URLParser('', self.data['url'])

    def insert_data(self):
        # print("DataInserter insert_data()")
        self.page = PageInserter(self.urlobj)
        WordInserter.insert_words(self.words, self.page.page)
        LinkInserter.insert_links(self.links, self.page.page)
        
        

    


