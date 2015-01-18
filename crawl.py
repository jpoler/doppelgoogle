# -*- coding: utf-8 -*-

import os
import sys
import db.models as models
from collections import deque
from urlparse import urlparse
from multiprocessing import Process, JoinableQueue, Lock, Pipe, active_children
from Queue import Empty, Full
import time
import urllib
from bs4 import BeautifulSoup
import traceback
from logger import prepare_log_dir, Logger, LOG_DIR
import signal


if sys.version < 3:
    range = xrange

import atexit

# @atexit.register
# def die():
#     print("Recieved an interrupt")

#     for child in active_children():
#         os.kill(child.pid, signal.SIGTERM)


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
        urlobj = URLAttrs(link["href"])
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

# most of this logic is borrowed
# probably need to remove anything after the "#"
class URLAttrs(object):
    def __init__(self, url):
        self.parse_url(url)
    
    def parse_url(self, url):
        fixed = fix_scheme(url)
        self.url = urlparse(fixed)
        (self.scheme, self.netloc, self.path,
         self.params, self.query, self.fragment) = self.url
        self.host, self.port = splitport(self.netloc)
        if "." in self.host and not is_ip_address(self.host):
            self.domain, self.tld  = self.host.rsplit(".", 1)
        else:
            self.domain = self.host
            self.tld = ""


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
        urlobj = URLAttrs(url)
        try:
            self.log.write_log("opening {}".format(url))
            connection = urllib.urlopen(urlobj.url.geturl())
        except IOError:
            return None

        finally:
            self.log.write_log("done with {}".format(url))
        if connection.headers["content-type"].find("text/html") == -1:
            return None
        soup = BeautifulSoup(connection.read())
        data["links"] = get_links(soup)
        data["words"] = get_text(soup)
        data["url"] = urlobj.url.geturl()
        del soup
        return data


    def run(self):

        while True:
            try:
                if self.pipe.poll():
                    message = self.pipe.recv()
                    if message == STOP:
                        self.log.write_log("quitting")
                        self.work_queue.close()
                        self.data_queue.close()
                        return

                # url = self.work_queue.get(True, BLOCK_TIME)
                while self.deque:
                    try:
                        d = self.deque.pop()
                        self.data_queue.put_nowait(d)
                        self.work_queue.task_done()
                    except Full:
                        self.deque.append(d)
                        break
                    except Exception as e:
                        print(e)


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
        self.done = LockDict()
        prepare_log_dir(LOG_DIR)
        self.log = Logger(LOG_DIR)
        self.links = deque()

    def insert_into_db(self, data):
        pass

    def stop_all_processes(self):
        for process, pipe in self.children:
            pipe.send(STOP)

    def violently_destroy_innocent_processes_and_then_self(self):
        for child in active_children():
            os.kill(child.pid, signal.SIGKILL)

        # this lets us skip the call to _exit_function where we block on children
        os.kill(os.getpid(), signal.SIGKILL)

    def run(self, seed):
        seed_url = URLAttrs(seed)
        self.work_queue.put(seed_url.url.geturl())

        self.children = []
        for _ in range(MAX_PROCESSES):
            master_pipe, child_pipe = Pipe()
            child = Worker(self.work_queue, self.data_queue,
                             self.done, child_pipe)
            child.start()
            self.children.append((child, master_pipe))

        successful_links = 0
        iterations = -1
        while True:
            iterations += 1
            # if iterations % 10000 == 0:
            #     print("Iterations: {}, successful_links: {}".format(iterations, successful_links))
            ### since this class is the only thing that can add to the queue,
            ### it is safe to kill all processess if queue is empty,
            ### but first must block until all tasks on work queue are processed
            ### in case more data is placed on the data queue, which results in more jobs

            if (self.work_queue.empty() and self.data_queue.empty()):
                self.work_queue.join()
                if self.data_queue.qsize() == 0:
                    for child, pipe in self.children:
                        pipe.send(STOP)
                    for child, pipe in self.children:
                        child.join()
                    break

            if not self.data_queue.empty():
                try:
                    data = self.data_queue.get_nowait()
                except Empty:
                    continue
                successful_links += 1

                self.links.append(data["links"])
                self.insert_into_db(data)
                self.done[data["url"]] = True

                # if database insertion fails, we want to say that we did it anyway,
                # because reprocessing the data is a waste because it will probably fail again

                # Ratio ends up being really lopsided and queue size gets huge while not many links
                # are processed. Fixing the problem by enforcing a 2:1 ratio of work_queue to data in the database
                if (self.work_queue.qsize() // successful_links) < 2:
                    links = self.links.pop()
                    for href in links:
                        # print("qsize {}, urls_done: {}, urls_deferred {}" \
                        #       "data_queue: {}".format(
                        #           self.work_queue.qsize(), successful_links, len(self.links),
                        #           self.data_queue.qsize()))
                        # print("work_queue_memsize: {} bytes, done_memsize: {} bytes, urls_deferred_memsize: {} bytes" \
                        #       "data_queue_memsize: {} bytes".format(
                        #           sys.getsizeof(self.work_queue), sys.getsizeof(self.done),
                        #           sys.getsizeof(self.links), sys.getsizeof(self.data_queue)))
                        if href not in self.done:
                            urlobj = URLAttrs(href)
                            self.work_queue.put(urlobj.url.geturl())

            # self.violently_destroy_innocent_processes_and_then_self()

if __name__ == "__main__":
    m = MasterOfPuppets()
    m.run("www.google.com")


