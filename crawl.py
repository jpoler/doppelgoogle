# -*- coding: utf-8 -*-

import db.models as models
from collections import defaultdict
from urlparse import urlparse
from multiprocessing import Process, JoinableQueue, Lock, Pipe
import time
import urllib
from bs4 import BeautifulSoup
import traceback

WHITESPACE = ['\n', '\t', ' ']
HTTP_SCHEME = "http://"
HTTPS_SCHEME = "https://"
TEST_SITE = "http://www.wikipedia.org"
UNWANTED_TAGS = set(['script', 'style'])
LINKS = ['a']
WANTED_LANGS = set(['en'])
UNWANTED_WORDS = set(['the', 'of', 'to', 'and', 'a', 'in', 'is', 'it'])

MAX_PROCESSES = 4
QUEUE_MAXSIZE = 1024

STOP = 1
KILL = 2


def word_generator(s):
    whitespace_handled = False
    start, stop = (0, 0)
    offset = 0
    for c in s:
        if whitespace_handled and c in WHITESPACE:
            yield (s[start:stop], offset)
            offset += 1
            whitespace_handled = False
            start = stop
        if c in WHITESPACE:
            start += 1
            stop += 1
            continue
        whitespace_handled = True
        stop += 1
    raise StopIteration

def fix_scheme(url):
    
    if (url.startswith(HTTP_SCHEME) or url.startswith(HTTPS_SCHEME)):
        return url
    url = url.lstrip('/')
    return HTTP_SCHEME + url



def get_links(soup):
    links = {}
    for link in soup.find_all('a'):
        if 'lang' in link.attrs:
            if link.attrs['lang'] not in WANTED_LANGS:
                continue
        if 'href' not in link.attrs:
            continue
        urlobj = URLAttrs(link['href'])
        links[urlobj.url.geturl()] = dict(link.attrs)
    return links

def get_text_only(soup):
    for script in soup.find_all(UNWANTED_TAGS):
        script.extract()
    return soup.get_text()

def digest_text(text):
    word_count = {}
    for word, offset in word_generator(text):
        if word not in UNWANTED_WORDS:
            freq, offsets = word_count.get(word, [0, []])
            offsets.append(offset)
            word_count[word] = [freq+1, offsets]
    return word_count

def get_text(soup):
    text_only = get_text_only(soup)
    return digest_text(text_only)

def is_ip_address(s):
    for i, octet in enumerate(s.split('.')):
        if not octet.isdigit():
            return False
        if not (0 <= int(octet) <= 255):
            return False
    return i == 3

def splitport(host):
    if host.count(':') == 1:
        return host.rsplit(':', 1)
    return (host, None)

# most of this logic is borrowed

# probably need to remove anything after the '#'
class URLAttrs(object):
    def __init__(self, url):
        self.parse_url(url)
    
    def parse_url(self, url):
        fixed = fix_scheme(url)
        self.url = urlparse(fixed)
        (self.scheme, self.netloc, self.path,
         self.params, self.query, self.fragment) = self.url
        self.host, self.port = splitport(self.netloc)
        if '.' in self.host and not is_ip_address(self.host):
            self.domain, self.tld  = self.host.rsplit('.', 1)
        else:
            self.domain = self.host
            self.tld = ''

def do_work(url):
    try:
        data = {}
        urlobj = URLAttrs(url)
        url_connection = urllib.urlopen(urlobj.url.geturl())
        soup = BeautifulSoup(url_connection.read())
        data['links'] = get_links(soup)
        data['words'] = get_text(soup)
        data['url'] = urlobj.url.geturl()
        del soup
    # is this block totally necessary?
    # what is being caught here that could not be caught in worker?
    # if do work fails, and we are sure that we mark the task as done on the work_queue
    # it is probably safe to just catch the exception and continue loop
    # maybe place a try except just within the infinite loop of worker

    except KeyboardInterrupt:
        raise
    except Exception as e:
        print("DO_WORK=================================================================DO_WORK")
        print(e)
        data = None
    finally:
        return data
        
def worker(work_queue, data_queue, done_urls, pipe, message_queue):
    try:
        sleeps = 0
        while True:
            if pipe.poll():
                message = pipe.recv()
                print("received message from master ", message)
                if message == STOP:
                    print("quitting")
                    # somehow this return does not terminate the process
                    # exitcode is None! meaning that the process hasn't terminated
                    # which explains why .join() blocks indefinitely
                    return
                time.sleep(1)
                sleeps += 1
                continue
            url = work_queue.get()
            # This try block is to catch errors and ensure that task_done is called no matter what
            try:
                data = do_work(url)
                if data is None:
                    message_queue.put("failed to process {}".format(url))
                else:
                    data_queue.put(data)
            except KeyboardInterrupt:
                raise
            finally:
                work_queue.task_done()
                                
    except KeyboardInterrupt as e:
        print("-------------------KEYBOARD INTERRUPT--------------------------")
        print("-------------------CHILD--------------------------")
        pipe.send(KILL)
        print("sent kill to master")
    except Exception as e:
        print("=================================WORKER========================================")
        print(e)
    finally:
        return None
        
class LockDict(dict):

    def __init__(self, *args, **kwargs):
        super(LockDict, self).__init__(*args, **kwargs)
        self.lock = Lock()

    def __getitem__(self, key):
        with self.lock:
            return super(LockDict, self).__getitem__(key)

    def __setitem__(self, key, value):
        with self.lock:
            super(LockDict, self).__setitem__(key, value)

    def __delitem__(self, key):
        with self.lock:
            super(LockDict, self).__delitem__(key)

class MasterOfPuppets(object):

    def __init__(self):
        self.work_queue = JoinableQueue(QUEUE_MAXSIZE)
        self.data_queue = JoinableQueue(QUEUE_MAXSIZE)
        self.done = LockDict()
        self.message_queue = JoinableQueue(QUEUE_MAXSIZE)

    def insert_into_db(self, data):
        pass

    def stop_all_processes(self):
        for p, pipe in self.crawlers:
            pipe.send(STOP)
        
    def run(self, seed):
        try:
            seed_url = URLAttrs(seed)
            self.work_queue.put(seed_url.url.geturl())
            
            self.crawlers = []
            for _ in xrange(MAX_PROCESSES):
                master_pipe, slave_pipe = Pipe()
                p = Process(target=worker,
                            args=(self.work_queue, self.data_queue,
                                  self.done, slave_pipe, self.message_queue))
                p.start()
                self.crawlers.append((p, master_pipe))


            while True:

                # check for messages from puppets
                for p, pipe in self.crawlers:
                    if pipe.poll():
                        message = pipe.recv()
                        print("Received message from child ", message)
                        if message == KILL:
                            raise KeyboardInterrupt
                
                
                ### since this class is the only thing that can add to the queue,
                ### it is safe to kill all processess if queue is empty,
                ### but first must block until all tasks on work queue are processed
                ### in case more data is placed on the data queue, which results in more jobs
                if self.work_queue.empty() and self.data_queue.empty():
                    self.work_queue.join()
                    if self.data_queue.empty():
                        for p, pipe in self.crawlers:
                            pipe.send(STOP)
                        for p, pipe in self.crawlers:
                            p.join()
                        break

                if not self.data_queue.empty():
                    data = self.data_queue.get()

                    # if database insertion fails, we want to say that we did it anyway,
                    # because reprocessing the data is a waste because it will probably fail again


                    for href in data['links']:
                        urlobj = URLAttrs(href)
                        if href not in self.done:
                            self.work_queue.put(urlobj.url.geturl())
                            # print(urlobj.url.geturl())

                    self.done[data['url']] = True

                    

                

            self.message_queue.put("all done")

            while not self.message_queue.empty():
                print(self.message_queue.get())
            
                    
        except KeyboardInterrupt as e:
            print("-------------------KEYBOARD INTERRUPT--------------------------")
            print("-------------------MASTER--------------------------")

            for p, pipe in self.crawlers:
                print(p.pid)
                pipe.send(STOP)

            for p, pipe in self.crawlers:
                p.join()
                print(p.exitcode)
            ## wtf?  proc need to explicitly return out of a caught exception?
            ## find out why
            print("returning")
            return

if __name__ == '__main__':
    m = MasterOfPuppets()
    m.run("www.google.com")
    
            

## How to safely kill all processes

## Make no assumptions about where the KeyboardInterrupt will be caught
## this is wrong, master should be the one to recieve signal i think but make sure

## if caught in master, send message to all children telling them to quit, and then
## block for each process until it dies

## if caught in child, send message to master through pipe notifying that a keyboard interrupt has been
## recieved, and clean up what was being done

## master must poll for messages at start of while True, and so must child


## RAGING CLUES:

## in emacs shell, the C-c interrupt isn't being caught consistantly
## in terminal window, C-c is caught first time
## after exit, bash never comes back, but is still running
## C-c becomes nonresponsive in both emacs and bash now

# (env)jdp@ThinkPad-T440s:~/dopplegoogle$ ps -A | grep pts/6
#  3369 pts/6    00:00:00 bash
#  3433 pts/6    00:00:01 python

# plain terminal
     # │         │         │      ├─gnome-terminal─┬─bash───python─┬─4*[python───2*[{python}]]
     # │         │         │      │                │               └─{python}
     # │         │         │      │                ├─bash───pstree
     # │         │         │      │                ├─gnome-pty-helpe
     # │         │         │      │                └─3*[{gnome-terminal}]


# within emacs
     # │         │         │      ├─emacs24─┬─bash───python─┬─4*[python───2*[{python}]]
     # │         │         │      │         │               └─{python}
     # │         │         │      │         └─2*[{emacs24}]

# http://stackoverflow.com/questions/21665341/python-multiprocessing-and-independence-of-children-processes
# this answer doesn't seem right? ive definitely experienced the parent quitting but children
# persist?

# signals?
# https://docs.python.org/2/library/signal.html

# atexit
