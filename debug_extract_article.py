# -*- coding: utf-8 -*-

import pickle
import os
import argparse
import importlib
import requests
from parser_helper import new_article


def parse_article(parser_module, article, article_origin, options):
    try:
        success, _need_serialize = parser_module.parse_article(
            article=article,
            response_text=article['body_full'],  # 'broken_html'
            logger=None)
        if success:
            if options.verbose:
                print(article['rss'])
            print("Succeed to parse: {}".format(article_origin))
        else:
            print("Fail to parse: {}".format(article_origin))
        return success
    except:
        print("Exception while parsing: {}".format(article_origin))
        return False


def safe_parse_article(parser_module, article, article_origin, options):
    while True:
        succeed = parse_article(parser_module, article, article_origin, options)
        if succeed or not options.infinite:
            return succeed
        else:
            importlib.reload(parser_module)


def parse_url(parser_module, url, options):
    try:
        headers = {
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.8,en-US;q=0.6,en;q=0.4',
            'Accept-Encoding': 'gzip,deflate'
        }
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise Exception(response)
        if parser_module.config.get('force_encoding'):
            response.encoding = parser_module.config['force_encoding']
        response_text = response.text
        feed_original = {
            'published_parsed': (2000, 1, 1, 0, 0, 0, 0, 0, 0),
            'title': 'fake title',
            'link': url,
            'author': 'fake author'
        }
        article = new_article(url, feed_original, body_full=response_text)
        return safe_parse_article(parser_module, article, url, options)
    except:
        print("Fail to parse: {}".format(url))
        return False


def parse_file(parser_module, filename, options):
    if os.path.isfile(filename):
        with open(filename, 'rb') as f:
            article = pickle.load(f)
    else:
        print('file not found %s' % filename)
        return
    return safe_parse_article(parser_module, article, filename, options)


def parse_all_files(parser_module, directory, options):
    files = [os.path.join(directory, f) for f in os.listdir(directory)
             if f.endswith('.html') and os.path.isfile(os.path.join(directory, f))]
    for f in files:
        parse_file(parser_module, f, options)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Web scraper')
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-i", "--infinite", help="infinite loop until parse succeed", action="store_true")
    parser.add_argument("-m", "--module", help="module file", required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-u", "--url", help="parse url", default=None)
    group.add_argument("-f", "--filename", help="parse file", default=None)
    group.add_argument("-d", "--directory", help="parse directory", default=None)
    args = parser.parse_args()
    module = importlib.import_module('parsers.' + args.module)
    if args.url:
        parse_url(module, args.url, args)
    elif args.filename:
        parse_file(module, args.filename, args)
    else:
        parse_all_files(module, args.directory, args)
