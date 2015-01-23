### current bpython session - file will be reevaluated, ### lines will not be run

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
words = first['words']
w = insert.WordInserter.insert_words(words, d.page.page)
### Traceback (most recent call last):
###   File "<input>", line 1, in <module>
###   File "/home/jdp/doppelgoogle/doppelgoogle/db/insert.py", line 185, in insert_words
###     connect_objects(page, word, **dct)
### TypeError: connect_objects() argument after ** must be a mapping, not list
last = data[-1]
### 
