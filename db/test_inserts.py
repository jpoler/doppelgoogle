# current bpython session - file will be reevaluated, ### lines will not be run

import doppelgoogle.db.insert as insert

from doppelgoogle.conf.conf import PICKLE_DUMP_PATH

import pickle
try:
    f = open(PICKLE_DUMP_PATH, 'r')
    data = pickle.load(f)
except Exception:
    f.close()
    print("Some sort of data error, quitting")
    exit(0)
else:
    f.close()

first = data[0]
d = insert.DataInserter(first)
d.insert_data()
### ['__class__', '__delattr__', '__dict__', '__doc__', '__format__', '__getattribute__', '__hash__', '__init__', '__module__', '__new_
### _', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_lookup_
### node_class', '_raw_class', 'build_manager', 'definition', 'manager', 'module_file', 'module_name']
### {'module_name': 'doppelgoogle.db.models', 'module_file': '/home/jdp/doppelgoogle/doppelgoogle/db/models.pyc', '_raw_class': 'WebPag
### e', 'manager': <class 'neomodel.cardinality.OneOrMore'>, 'definition': {'direction': 1, 'node_class': <class 'doppelgoogle.db.model
### s.WebPage'>, 'model': None, 'relation_type': 'DOMAIN_CONTAINS_WEBPAGE'}}
### ['__bool__', '__class__', '__contains__', '__delattr__', '__dict__', '__doc__', '__format__', '__getattribute__', '__getitem__', '_
### _hash__', '__init__', '__iter__', '__len__', '__module__', '__new__', '__nonzero__', '__reduce__', '__reduce_ex__', '__repr__', '__
### setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_check_node', '_in_node_set', '_set_start_end_cls', 'all',
###  'connect', 'definition', 'description', 'disconnect', 'filters', 'get', 'is_connected', 'match', 'name', 'reconnect', 'relationshi
### p', 'search', 'single', 'source', 'source_class', 'target_class']
### pages
### ['__class__', '__delattr__', '__dict__', '__doc__', '__format__', '__getattribute__', '__hash__', '__init__', '__module__', '__new_
### _', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_lookup_
### node_class', '_raw_class', 'build_manager', 'definition', 'manager', 'module_file', 'module_name']
### {'module_name': 'doppelgoogle.db.models', 'module_file': '/home/jdp/doppelgoogle/doppelgoogle/db/models.pyc', '_raw_class': 'Subdom
### ain', 'manager': <class 'neomodel.cardinality.OneOrMore'>, 'definition': {'direction': 1, 'node_class': <class 'doppelgoogle.db.mod
### els.Subdomain'>, 'model': None, 'relation_type': 'DOMAIN_CONTAINS_SUBDOMAIN'}}
### ['__bool__', '__class__', '__contains__', '__delattr__', '__dict__', '__doc__', '__format__', '__getattribute__', '__getitem__', '_
### _hash__', '__init__', '__iter__', '__len__', '__module__', '__new__', '__nonzero__', '__reduce__', '__reduce_ex__', '__repr__', '__
### setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_check_node', '_in_node_set', '_set_start_end_cls', 'all',
###  'connect', 'definition', 'description', 'disconnect', 'filters', 'get', 'is_connected', 'match', 'name', 'reconnect', 'relationshi
### p', 'search', 'single', 'source', 'source_class', 'target_class']
### subdomain
### ['__class__', '__delattr__', '__dict__', '__doc__', '__format__', '__getattribute__', '__hash__', '__init__', '__module__', '__new_
### _', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_lookup_
### node_class', '_raw_class', 'build_manager', 'definition', 'manager', 'module_file', 'module_name']
### {'module_name': 'doppelgoogle.db.models', 'module_file': '/home/jdp/doppelgoogle/doppelgoogle/db/models.pyc', '_raw_class': 'TopLev
### elDomain', 'manager': <class 'neomodel.cardinality.OneOrMore'>, 'definition': {'direction': 1, 'node_class': <class 'doppelgoogle.d
### b.models.TopLevelDomain'>, 'model': None, 'relation_type': 'TLD_CONTAINS_DOMAIN'}}
### ['__bool__', '__class__', '__contains__', '__delattr__', '__dict__', '__doc__', '__format__', '__getattribute__', '__getitem__', '_
### _hash__', '__init__', '__iter__', '__len__', '__module__', '__new__', '__nonzero__', '__reduce__', '__reduce_ex__', '__repr__', '__
### setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_check_node', '_in_node_set', '_set_start_end_cls', 'all',
###  'connect', 'definition', 'description', 'disconnect', 'filters', 'get', 'is_connected', 'match', 'name', 'reconnect', 'relationshi
### p', 'search', 'single', 'source', 'source_class', 'target_class']
### tld
words = first['words']
w = insert.WordInserter.insert_words(words, d.page)
### (u'project', 1, [54])
### <doppelgoogle.db.models.Word object at 0x7f12723df9d0>
### (u'visit', 1, [40])
### <doppelgoogle.db.models.Word object at 0x7f126ec2e7d0>
### (u'seconds.', 1, [36])
### <doppelgoogle.db.models.Word object at 0x7f1271b86390>
### (u'\u2013', 1, [7])
### (u'redirected', 1, [32])
### <doppelgoogle.db.models.Word object at 0x7f1273a03210>
### (u'our', 1, [20])
### <doppelgoogle.db.models.Word object at 0x7f1273a03ed0>
### (u'You', 1, [28])
### <doppelgoogle.db.models.Word object at 0x7f1273a03390>
### (u'Main', 1, [42])
### <doppelgoogle.db.models.Word object at 0x7f1273a03e10>
### (u'find', 1, [15])
### <doppelgoogle.db.models.Word object at 0x7f1273a03710>
### (u'information', 1, [47])
### <doppelgoogle.db.models.Word object at 0x7f1273a03790>
### (u'We', 1, [12])
### <doppelgoogle.db.models.Word object at 0x7f1273a03950>
### (u'there', 1, [33])
### <doppelgoogle.db.models.Word object at 0x7f1273a03d90>
### (u'http://en.wikipedia.org/wiki/Computer?', 1, [27])
### <doppelgoogle.db.models.Word object at 0x7f1273a036d0>
### (u'Did', 1, [22])
### <doppelgoogle.db.models.Word object at 0x7f1273a03250>
### (u'404', 1, [6])
### (u'above', 1, [17])
### <doppelgoogle.db.models.Word object at 0x7f1273a03350>
### (u'you', 2, [23, 38])
### <doppelgoogle.db.models.Word object at 0x7f1273a03110>
### (u'type', 2, [26, 50])
### <doppelgoogle.db.models.Word object at 0x7f1273a03a10>
### (u'servers.', 1, [21])
### <doppelgoogle.db.models.Word object at 0x7f1273a03a90>
### (u'more', 1, [46])
### <doppelgoogle.db.models.Word object at 0x7f127391ab50>
### (u'A', 1, [53])
### <doppelgoogle.db.models.Word object at 0x7f127391a210>
### (u'be', 1, [30])
### <doppelgoogle.db.models.Word object at 0x7f127391ad90>
### (u'Foundation', 1, [58])
### <doppelgoogle.db.models.Word object at 0x7f127391a150>
### (u'found:', 1, [3])
### <doppelgoogle.db.models.Word object at 0x7f127391ad50>
### (u'error.', 1, [52])
### <doppelgoogle.db.models.Word object at 0x7f127391a390>
### (u'five', 1, [35])
### <doppelgoogle.db.models.Word object at 0x7f127391a8d0>
### (u'Error', 1, [5])
### <doppelgoogle.db.models.Word object at 0x7f127391a5d0>
### (u'not', 3, [2, 9, 14])
### <doppelgoogle.db.models.Word object at 0x7f127391a190>
### (u'Page', 1, [43])
### <doppelgoogle.db.models.Word object at 0x7f127391ae90>
### (u'on', 1, [19])
### <doppelgoogle.db.models.Word object at 0x7f127391a9d0>
### (u'about', 1, [48])
### <doppelgoogle.db.models.Word object at 0x7f127391acd0>
### (u'read', 1, [45])
### <doppelgoogle.db.models.Word object at 0x7f127391aa50>
### (u'Wikimedia', 2, [0, 57])
### <doppelgoogle.db.models.Word object at 0x7f1273a10750>
### (u'could', 1, [13])
### <doppelgoogle.db.models.Word object at 0x7f1273a10a90>
### (u'http://en.wikipedia.org/Computer', 2, [4, 11])
### <doppelgoogle.db.models.Word object at 0x7f1273a10d10>
### (u'Alternatively,', 1, [37])
### <doppelgoogle.db.models.Word object at 0x7f1273a10690>
### (u'or', 1, [44])
### <doppelgoogle.db.models.Word object at 0x7f1273a10610>
### (u'will', 1, [29])
### <doppelgoogle.db.models.Word object at 0x7f1273a10850>
### (u'this', 1, [49])
### <doppelgoogle.db.models.Word object at 0x7f1273a10410>
### (u'can', 1, [39])
### <doppelgoogle.db.models.Word object at 0x7f1273a10e50>
### (u'File', 1, [8])
### <doppelgoogle.db.models.Word object at 0x7f1273a101d0>
### (u'found', 1, [10])
### <doppelgoogle.db.models.Word object at 0x7f1273a10410>
### (u'page', 2, [1, 18])
### <doppelgoogle.db.models.Word object at 0x7f1273a10a10>
### (u'automatically', 1, [31])
### <doppelgoogle.db.models.Word object at 0x7f1273a107d0>
### (u'mean', 1, [24])
### <doppelgoogle.db.models.Word object at 0x7f127391af90>
### 


