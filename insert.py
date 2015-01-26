import doppelgoogle.db.query as query
from doppelgoogle.db.repr import *

class PageInserter(object):

    def __init__(self, data_inserter):
        self.data_inserter = data_inserter
        self.urlobj = self.data_inserter.urlobj
        self.query = self.data_inserter.query

    def handle_all():
        domain_repr = DomainRepr(name=self.urlobj.domain)
        subdomain_repr = SubdomainRepr(name=self.urlobj.subdomain)
        tld_repr = TLDRepr(name=self.urlobj.tld)
        self.query.merge_node(domain_repr)
        self.query.merge_node(subdomain_repr)
        self.query.merge_node(tld_repr)
        self.query.merge_relation(domain_repr, subdomain_repr, 'SUBDOMAIN_OF_DOMAIN')
        self.query.merge_relation(domain_repr, tld_repr, 'TLD_OF_DOMAIN')

        self.query.create_relation(self.page, subdomain_repr, 'SUBDOMAIN_OF_PAGE')
        self.query.create_relation(self.page, tld_repr, 'TLD_OF_PAGE')

        self.query.merge_relation(domain_repr, self.page, 'DOMAIN_CONTAINS_PAGE')
        
    def insert_page(self):
        self.page = PageRepr(name=self.urlobj.url.geturl())
        self.page_inserter.merge_node(self.page)
        self.handle_all()

class 

        

class WordInserter(object):

    def __init__(self, data_inserter):
        self.data_inserter = data_inserter

class LinkInserter(object):

    def __init__(self, data_inserter):
        self.data_inserter = data_inserter


class DataInserter(object):

    def __init__(self, data, graph):
        # print("DataInserter __init__")
        self.graph = graph
        self.data = data
        self.query = InsertQuery(self.graph)
        self.domains = set()
        self.subdomains = set()
        self.tlds = set()
        self.url = data['url']
        self.words = data['words']
        self.links = data['links']
        self.urlobj = URLParser('', self.data['url'])

    def insert_data(self):

        self.page_inserter = PageInserter(self)
        self.page_inserter.insert_page()

        





        #instead hand self
        # WordInserter.insert_words(self.words, self.page.page)
        # LinkInserter.insert_links(self.links, self.page.page)
