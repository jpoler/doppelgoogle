# -*- coding: utf-8 -*-

import db.models as models
from collections import defaultdict
from urlparse import urlparse
from multiprocessing import Process, JoinableQueue, Lock, Pipe
from Queue import Full
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
BLOCK_TIME = 1

MAX_PROCESSES = 4
QUEUE_MAXSIZE = 1024

# constants for message passing
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

def process_url(url):
    data = {}
    urlobj = URLAttrs(url)
    try:
        connection = urllib.urlopen(urlobj.url.geturl())
    except IOError:
        return None
    soup = BeautifulSoup(connection.read())
    data['links'] = get_links(soup)
    data['words'] = get_text(soup)
    data['url'] = urlobj.url.geturl()
    del soup
    return data

class Worker(Process):

    def __init__(self, work_queue, data_queue, done_urls, pipe, *args, **kwargs):
        super(Worker, self).__init__(*args, **kwargs)
        self.work_queue = work_queue
        self.data_queue = data_queue
        self.pipe = pipe

    def run(self):
        while True:
            try:
                got_from_work_queue = 0
                if self.pipe.poll():
                    message = self.pipe.receive
                    if message == STOP:
                        print("quitting")
                        self.work_queue.close()
                        self.data_queue.close()
                        return

                url = self.work_queue.get(True, BLOCK_TIME)

                got_from_work_queue = 0
                data = process_url(url)
                if data:
                    self.data_queue.put(data, BLOCK_TIME)
            # It is ugly to catch such a broad swathe of exceptions
            # but the show must go on.
            except Full:
                if got_from_work_queue:
                    try:
                        self.work_queue.put_nowait(url)
                    except:
                        pass
                continue
            except Exception as e:
                print("Exception", e)
                continue
            finally:
                # call task_done no matter what so that master can join on work_queue
                # if we don't make sure that this gets called, then work_queue.join()
                # will block indefinitely
                if got_from_work_queue:
                    self.work_queue.task_done()
      
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

    def insert_into_db(self, data):
        pass

    def stop_all_processes(self):
        for process, pipe in self.children:
            pipe.send(STOP)
        
    def run(self, seed):
        try:
            seed_url = URLAttrs(seed)
            self.work_queue.put(seed_url.url.geturl())
            
            self.children = []
            for _ in xrange(MAX_PROCESSES):
                master_pipe, child_pipe = Pipe()
                child = Worker(self.work_queue, self.data_queue,
                                 self.done, child_pipe)
                child.start()
                self.children.append((child, master_pipe))

            while True:
                ### since this class is the only thing that can add to the queue,
                ### it is safe to kill all processess if queue is empty,
                ### but first must block until all tasks on work queue are processed
                ### in case more data is placed on the data queue, which results in more jobs
                if self.work_queue.empty() and self.data_queue.empty():
                    self.work_queue.join()
                    if self.data_queue.empty():
                        for child, pipe in self.children:
                            pipe.send(STOP)
                        for child, pipe in self.children:
                            child.join()
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
 
        except KeyboardInterrupt as e:
            print("-------------------KEYBOARD INTERRUPT--------------------------")
            print("-------------------MASTER--------------------------")
            self.work_queue.close()
            self.data_queue.close()
            
            for child, pipe in self.children:
                pipe.send(STOP)

            for child, pipe in self.children:
                child.join()

if __name__ == '__main__':
    m = MasterOfPuppets()
    m.run("www.google.com")
