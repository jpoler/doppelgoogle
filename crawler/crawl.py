# -*- coding: utf-8 -*-

import os
import sys

from collections import deque
from urlparse import urlparse, urljoin
from multiprocessing import Process, JoinableQueue, Lock, Pipe, active_children
from Queue import Empty, Full
import time
import urllib
from bs4 import BeautifulSoup
import traceback

import signal

import doppelgoogle.db.models as models
from doppelgoogle.conf.conf import SETTINGS
from doppelgoogle.log.log import prepare_log_dir, Logger, LOG_DIR
from doppelgoogle.db.size import database_size
from doppelgoogle.exceptions.exceptions import URLParseException


if sys.version < 3:
    range = xrange


WHITESPACE = set(["\n", "\t", " "])
HTTP_SCHEME = "http://"
HTTPS_SCHEME = "https://"
TEST_SITE = "http://www.wikipedia.org"
UNWANTED_TAGS = set(["script", "style"])
LINKS = ["a"]
WANTED_LANGS = set(["en"])
UNWANTED_WORDS = set(["the", "of", "to", "and", "a", "in", "is", "it"])
BLOCK_TIME = 1

MAX_PROCESSES = 4
QUEUE_MAXSIZE = 2**20

# constants for message passing
STOP = 1
KILL = 2

LOG_DIR = os.path.join("/tmp", "crawl")

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
    url = url.lstrip("/")
    return HTTP_SCHEME + url

def get_links(soup):
    links = {}
    for link in soup.find_all("a"):
        if "lang" in link.attrs:
            if link.attrs["lang"] not in WANTED_LANGS:
                continue
        if "href" not in link.attrs:
            continue
        url = link["href"]
        links[url] = dict(link.attrs)
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
    for i, octet in enumerate(s.split(".")):
        if not octet.isdigit():
            return False
        if not (0 <= int(octet) <= 255):
            return False
    return i == 3

def splitport(host):
    if host.count(":") == 1:
        return host.rsplit(":", 1)
    return (host, None)

def get_parsed_url(base_url, url):
    try:
        urlobj = URLParser(base_url, url)
        print(urlobj.url.geturl())        
        return urlobj

    except URLParseException as e:
        print(e)
        return None
    
class URLParser(object):
    def __init__(self, base_url, url):
        self.parse_url(base_url, url)
    
    def parse_url(self, base_url, url):
        url = urljoin(base_url, url)
        fixed = fix_scheme(url)
        self.url = urlparse(fixed)
        (self.scheme, self.netloc, self.path,
         self.params, self.query, self.fragment) = self.url
        self.host, self.port = splitport(self.netloc)
        if self.scheme and self.host.count(".") == 2 and not is_ip_address(self.host):
            self.subdomain, self.domain, self.suffix  = self.host.split(".")
        else:
            raise URLParseException

class Worker(Process):

    def __init__(self, work_queue, data_queue, done_urls, pipe, *args, **kwargs):
        super(Worker, self).__init__(*args, **kwargs)
        self.work_queue = work_queue
        self.data_queue = data_queue
        self.pipe = pipe
        self.log = Logger(LOG_DIR)
        self.deque = deque()

    def process_url(self, url):
        data = {}
        try:
            connection = urllib.urlopen(url)
        except IOError:
            return None

        if connection.headers["content-type"].find("text/html") == -1:
            return None
        soup = BeautifulSoup(connection.read())
        data["links"] = get_links(soup)
        data["words"] = get_text(soup)
        data["url"] = url
        del soup
        return data

    def run(self):
        while True:
            try:
                if self.pipe.poll():
                    message = self.pipe.recv()
                    if message == STOP:
                        print("quitting", self.pid)
                        self.log.write_log("quitting")
                        self.log.flush()
                        self.work_queue.close()
                        self.data_queue.close()
                        return

                while self.deque:
                    try:
                        d = self.deque.pop()
                        self.data_queue.put_nowait(d)
                        self.work_queue.task_done()
                    except Full:
                        self.deque.append(d)
                        break

                try:
                    url = self.work_queue.get_nowait()
                except Empty:
                    continue
                data = self.process_url(url)
                if data:
                    self.deque.append(data)
                else:
                    self.work_queue.task_done()

            except Exception as e:
                traceback.print_exc()
                continue
     
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
        self.pipes = {}
        self.done = LockDict()
        prepare_log_dir(LOG_DIR)
        self.log = Logger(LOG_DIR)
        self.links = deque()
        self.valid_urls = deque()
        self.attrs = set()
        # testing hack
        self.data_threshold = 200000
        # self.data_threshold = SETTINGS['MAX_DATABASE_SIZE'] - database_size()
        print(SETTINGS['MAX_DATABASE_SIZE'])
        print(database_size())
        if self.data_threshold <= 0:
            print("Database is already larger than max size")
            self.log.write_log("Database is already larger than max size")
            exit(1)
        self.data_written = 0

    def insert_into_db(self, data):
        for link in data['links']:
            self.attrs.update(set(data['links'][link].keys()))

    def get_pipe(self, child):
        try:
            return self.pipes[child.pid]
        except KeyError:
            return None

    # may want to store a pipe under pid instead of in my own list, then active_children()
    # can be used which is certainly safer
    def nicely_ask_children_to_stop(self):
        for child in active_children():
            pipe = self.get_pipe(child)
            if pipe:
                pipe.send(STOP)

        for child in active_children():
            child.join()

    def run(self, seed):
        seed_url = get_parsed_url('', seed)
        if not seed_url:
            raise URLParseException("Cannot parse seed URL, which is a bit of a problem\n{}".format(seed))
        self.work_queue.put(seed_url.url.geturl())

        for _ in range(MAX_PROCESSES):
            master_pipe, child_pipe = Pipe()
            child = Worker(self.work_queue, self.data_queue,
                             self.done, child_pipe)
            child.start()
            self.pipes[child.pid] = master_pipe

        successful_links = 0
        iterations = -1
        while True:
            iterations += 1
            # if iterations % 10000 == 0:
            #     print("Iterations: {}, successful_links: {}".format(iterations, successful_links))
            if self.data_written > self.data_threshold:
#                if database_size() > self.data_threshold:
                self.nicely_ask_children_to_stop()
                break

            while self.valid_urls:
                try:
                    url = self.valid_urls.pop()
                    self.work_queue.put_nowait(url)
                except Full:
                    self.deque.append(url)
                    break

            if (self.work_queue.empty() and self.data_queue.empty() and not self.valid_urls):
                self.work_queue.join()
                if self.data_queue.qsize() == 0:
                    self.nicely_ask_children_to_stop()
                    break

            if self.data_queue.qsize() != 0:
                try:
                    data = self.data_queue.get_nowait()
                    self.data_queue.task_done()
                except Empty:
                    continue
                successful_links += 1

                self.links.append(data["links"])
                self.insert_into_db(data)
                print(self.attrs)
                self.done[data["url"]] = True
                self.data_written += sys.getsizeof(data)

                # Ratio ends up being really lopsided and queue size gets huge while not many links
                # are processed. Fixing the problem by enforcing a 2:1 ratio of work_queue to data in the database
                if (self.work_queue.qsize() // successful_links) < 2:
                    links = self.links.pop()
                    for href in links:
                        if href not in self.done:
                            urlobj = get_parsed_url(data["url"], href)
                            if urlobj:
                                self.valid_urls.append(urlobj.url.geturl())


def run(seed):
    m = MasterOfPuppets()
    m.run(seed)
