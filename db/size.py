import os

from doppelgoogle.conf.conf import SETTINGS

def directory_size(path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

def database_size():
    return directory_size(SETTINGS['DATABASE_PATH'])


if __name__ == "__main__":
    print(database_size())
