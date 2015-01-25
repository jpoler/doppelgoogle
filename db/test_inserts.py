### current bpython session - file will be reevaluated, ### lines will not be run
import sys
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

for datum in data[:2]:
    
    print(sys.getsizeof(datum))
    print("inserting {}".format(datum['url']))
    insert.DataInserter(datum).insert_data()
