import os
import sys
import datetime
from multiprocessing import Process
import time

if sys.version < 3:
    range = xrange


TEMP_DIR = '/tmp'
LOG_DIR = os.path.join(TEMP_DIR, "crawl")

def _mkdir(newdir):
    """works the way a good mkdir should :)
    - already exists, silently complete
    - regular file in the way, raise an exception
    - parent directory(ies) does not exist, make them as well
    """
    if os.path.isdir(newdir):
        pass
    elif os.path.isfile(newdir):
        raise OSError("a file with the same name as the desired " \
                      "dir, '%s', already exists." % newdir)
    else:
        head, tail = os.path.split(newdir)
        if head and not os.path.isdir(head):
            _mkdir(head)
            #print "_mkdir %s" % repr(newdir)
        if tail:
            os.mkdir(newdir)

def prepare_log_dir(dir):
    if not os.path.exists(dir):
        _mkdir(dir)
        return
    for f in os.listdir(dir):
        path = os.path.join(dir, f)
        if os.path.isfile(path):
            os.remove(path)

class Logger:
    def __init__(self, dir):
        self.filepath = os.path.join(dir, str(os.getpid()))
        if os.path.exists(dir):
            self.file = open(self.filepath, "w")
        else:
            _mkdir(dir)
            self.file = open(self.filepath, "w")

    def write_log(self, message):
        try:
            self.file.write("{}\t{}\t{}\n".format(
                datetime.datetime.now().strftime("%H%M%S%f"),
                os.getpid(),
                message
            ))
        except IOError as e:
            print("Failure to write to log, pid: {}".format(os.getpid()))

    def flush(self):
        self.file.flush()


def test_logger():
    time.sleep(1)
    log = Logger(LOG_DIR)
    for i in range(10):
        log.write_log("BOOP")

if __name__ == "__main__":
    prepare_log_dir(LOG_DIR)
    children = [Process(target=test_logger, args=()) for i in range(10)]
    for child in children:
        child.start()

    parent_log = Logger(LOG_DIR)

    for i in range(50):
        parent_log.write_log("BEEP")

    for child in children:
        child.join()
                   
        
    
