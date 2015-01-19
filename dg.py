from __future__ import print_function

import argparse
import sys


from crawler.crawl import run as crawler_run

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Command-line interface for doppelgoogle.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--crawl", help="usage: python dg.py --crawl <SEED_URL>",
                       action='store_true')
    group.add_argument("--server", help="usage: python dg.py --server <HOSTNAME> <PORT>",
                       action='store_true')
    parser.add_argument("args", nargs="*", default=[], help="Arguments to command.")
    args = parser.parse_args()

    if args.crawl:
        if len(args.args) != 1:
            print("Invalid arguments: usage: python dg.py --crawl <SEED_URL>", file=sys.stderr)
            exit(1)
        crawler_run(*args.args)
    elif args.server:
        if len(args.args) != 2:
            print("Invalid arguments: usage: python dg.py --server <HOSTNAME> <PORT>", file=sys.stderr)
            exit(1)
        raise NotImplementedError
