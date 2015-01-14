import db.models as models
from collections import defaultdict
from itertools import chain
from urlparse import urlparse
from multiprocessing Process, Queue

import time
WHITESPACE = ['\n', '\t', ' ']
HTTP_SCHEME = "http://"
HTTPS_SCHEME = "https://"
TEST_SITE = "http://www.wikipedia.org"
UNWANTED_TAGS = ['script', 'style']
LINKS = ['a']
WANTED_LANGS = ['en']

MAX_PROCESSES = 4
QUEUE_MAXSIZE = 1024



import urllib
from bs4 import BeautifulSoup

def word_generator(s):
    whitespace_handled = False
    start, stop = (0, 0)
    for c in s:
        if whitespace_handled and c in WHITESPACE:
            yield s[start:stop]
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
    return HTTP_SCHEME + url

def get_links(soup):
    for link in soup.find_all(LINKS):
        if 'lang' in link.attrs:
            if link.attrs['lang'] not in WANTED_LANGS:
                continue
            else:
                print link

def get_text_only(soup):
    for script in soup.find_all(UNWANTED_TAGS):
        script.extract()
    return soup.get_text()

def digest_text(text):
    word_count = defaultdict(lambda: 0)
    for word in word_generator(text):
        word_count[word] += 1
    return word_count

def get_text(soup):
    text_only = get_text_only(soup)
    return digest_text(text_only)

def is_ip_address(s):
    for i, octet in enumerate(s.split('.')):
        if not (0 <= int(octet) <= 255):
            return False
    return i == 3

def splitport(host):
    return host.split(':')
    
def parse_url(url):
    fixed = fix_scheme(url)
    parsed = urlparse.urlparse(fixed)
    (scheme, netloc, path,
     params, query, fragment) = parsed
    
    
    

def worker(work_queue, data_queue):
    data = {}
    while True:
        if work_queue.empty():
            time.sleep(5)
            continue
        url = work_queue.get()
        
        url_connection = urllib.urlopen(url.geturl())
        soup = BeautifulSoup(url_connection.read())
        data['links'] = get_links(soup)
        data['words'] = get_text(soup)
        data['url'] = url.geturl()
        data['scheme'] = url.scheme
        domain, port = 
        data['domain'] = url.netloc

        data[
        del soup
        


class CrawlerManager(multiprocessing.Manager):

    def __init__(self, *args, **kwargs):
        
        
if __name__ == '__main__':
    
    work_queue = Queue(QUEUE_MAXSIZE)
    data_queue = Queue(QUEUE_MAXSIZE)
    work_queue.put(TEST_SITE)
    
    crawlers = [Process(target=worker, args=(work_queue, data_queue))
                for _ in range(MAX_PROCESSES)]
    c.start()
    c.join()
    
