import sys
import pickle
from py2neo import Graph

import doppelgoogle.db.query as query
from doppelgoogle.db.repr import *
from doppelgoogle.conf.conf import PICKLE_DUMP_PATH

import datetime

try:
    f = open(PICKLE_DUMP_PATH, 'rb')
    data = pickle.load(f)
except Exception:
    f.close()
    print("Some sort of data error, quitting")
    exit(1)
else:
    f.close()

g = Graph()
tx = g.cypher.begin()


uq = query.UniquenessConstraintQuery(g)
constraints = [
    {'label': 'WebPage', 'prop': 'name'},
    {'label': 'Word', 'prop':'name'},
    {'label': 'Domain', 'prop':'name'},
    {'label': 'Subdomain', 'prop':'name'},
    {'label': 'TLD', 'prop':'name'},
]

print(uq.add_constraints_and_execute(constraints))

# iq = query.IndexQuery(g)
# indexes = [
#     {'label': 'WebPage', 'prop': 'name'},
#     {'label': 'Word', 'prop':'name'},
#     {'label': 'Domain', 'prop':'name'},
#     {'label': 'Subdomain', 'prop':'name'},
#     {'label': 'TLD', 'prop':'name'},
# ]

# iq.add_indexes_and_execute(indexes)


page_repr1 = WebPageRepr(name='http://en.wikipedia.org/wiki/Computer')
page_repr2 = WebPageRepr(name='http://www.google.com')
link_repr1 = LinkRepr(href='http://www.google.com', lang='en')

q = query.InsertQuery(g)
q.merge_node(page_repr1)
q.merge_node(page_repr2)
q.create_relation(page_repr1, page_repr2, 'LINKS_TO', attrs=link_repr1)
q.query.append("RETURN n1")
q.execute()




