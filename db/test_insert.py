import sys
import pickle
from py2neo import Graph

import doppelgoogle.db.insert as insert
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

# q = insert.InsertQuery(g)

uq = insert.UniquenessConstraintQuery(g)
constraints = [
    {'label': 'WebPage', 'prop': 'name'},
    {'label': 'Word', 'prop':'name'},
    {'label': 'Domain', 'prop':'name'},
    {'label': 'Subdomain', 'prop':'name'},
    {'label': 'TLD', 'prop':'name'},
]

print(uq.add_constraints_and_execute(constraints))

# iq = insert.IndexQuery(g)
# indexes = [
#     {'label': 'WebPage', 'prop': 'name'},
#     {'label': 'Word', 'prop':'name'},
#     {'label': 'Domain', 'prop':'name'},
#     {'label': 'Subdomain', 'prop':'name'},
#     {'label': 'TLD', 'prop':'name'},
# ]

# iq.add_indexes_and_execute(indexes)


page_repr1 = WebPageRepr(name='http://en.wikipedia.org/wiki/Computer')
page_repr2 = WebPageRepr(name='foo')

q.merge_statement(page_repr1)
q.merge_statement(page_repr2)
q.query.append("RETURN n1")
q.execute()


