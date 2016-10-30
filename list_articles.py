# -*- coding: utf-8 -*-
"""
Display list of articles
(python 3)
"""

import pickle
import os.path
import datetime
import argparse


def run(args):
    cache_filename = os.path.join(args.dir, "articles.cache")
    if not os.path.isfile(cache_filename):
        print("error : file not found {}".format(cache_filename))
        exit(-1)

    # load cache
    with open(cache_filename, 'rb') as f:
        articles_cache = pickle.load(f)

    # sort by date
    articles = [articles_cache[url] for url in articles_cache]
    for article in articles:
        daytime = article.get('last_date_parsed', None)
        if daytime:
            article['day'] = daytime.date()
        else:
            article['day'] = datetime.date(1970, 1, 1)
    sorted(articles, key=lambda article: article['day'])

    # display articles titles
    cur_day = None
    for article in articles:
        if article['day'] != cur_day:
            print("\n\n{} :\n------------".format(article['day']))
            cur_day = article['day']
        title = article.get('title', '')
        if title is None:
            title = ''
        print(title)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Web scraper')
    parser.add_argument("-d", "--dir",
                        help="cache data directory ex: /var/spiders/rss/data/<name>",
                        required=True)
    args = parser.parse_args()
    run(args)
