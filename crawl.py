import db.models as models
from collections import defaultdict
from itertools import chain
from urlparse import urlparse
from multiprocessing import Process, Queue

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
        if not octet.isdigit():
            return False
        if not (0 <= int(octet) <= 255):
            return False
    return i == 3

def splitport(host):
    if host.count(':') == 1:
        return host.rsplit('.', 1)
    return host, None



# most of this logic is borrowed
class URLAttrs(object):
    def __init__(self, url):
        self.parse_url(url)
    
    def parse_url(self, url):
        fixed = fix_scheme(url)
        self.url = urlparse(fixed)
        print(type(self.url))
        (self.scheme, self.netloc, self.path,
         self.params, self.query, self.fragment) = self.url
        self.host, self.port = splitport(self.netloc)
        if '.' in self.host and not is_ip_address(self.host):
            self.domain, self.tld  = self.host.rsplit('.', 1)
        else:
            self.domain = self.host
            self.tld = ''
    
def worker(work_queue, data_queue):
    data = {}
    sleeps = 0
    while True:
        if sleeps > 5:
            break
        if work_queue.empty():
            print(work_queue)
            time.sleep(1)
            sleeps += 1
            continue
        urlobj = work_queue.get()
        url_connection = urllib.urlopen(urlobj.url.geturl())
        soup = BeautifulSoup(url_connection.read())
        data['links'] = get_links(soup)
        data['words'] = get_text(soup)
        data['url'] = urlobj
        data_queue.put(urlobj.url.geturl())
        del soup
        break
        


if __name__ == '__main__':
    
    work_queue = Queue(QUEUE_MAXSIZE)
    data_queue = Queue(QUEUE_MAXSIZE)
    work_queue.put(URLAttrs(TEST_SITE))

    try:
        crawlers = [Process(target=worker, args=(work_queue, data_queue))
                    for _ in range(MAX_PROCESSES)]
        
    
        for crawler in crawlers:
            crawler.start()
            
        print("work is happening")
            
        for crawler in crawlers:
            crawler.join()
        print(data_queue.get())
    except KeyboardInterrupt as e:
        if hasattr(__module__, crawlers):
            for crawler in crawlers:
                crawler.join()
        print("GOODFLKJSDFLKJSDLFKJSFDL")
        
