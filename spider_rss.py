# -*- coding: utf-8 -*-
"""
Web Spider for news web site
This program crawl a web sites to collect a list of articles
Produces an xml rss file
Using Python 3.4
"""

import logging
import datetime
import numpy as np
from sys import platform
import requests
from parser_helper import new_article, build_feed
import feedparser
import pickle
import os.path
from os import chmod
import hashlib
from time import sleep
from tqdm import tqdm
from sys import version_info
import glob
import importlib


# region globals
if platform == "win32":
    LOG_DIRECTORY = 'C:\\dev\\rss-scrapper\\rss\\log\\{site}\\'
    DATA_DIRECTORY = 'C:\\dev\\rss-scrapper\\rss\\data\\{site}\\'
    FEED_DIRECTORY = 'C:\\dev\\rss-scrapper\\rss\\feed\\{site}\\'
else:
    LOG_DIRECTORY = '/var/log/spiders/rss/{site}/'
    DATA_DIRECTORY = '/var/spiders/rss/data/{site}/'
    FEED_DIRECTORY = '/var/www/rss/{site}/'

VERBOSE = True

TODAY = str(datetime.datetime.now())[:10]

IS_PYTHON_3 = version_info >= (3, 0)
# endregion globals


def get_rnd_from_tuple(array_of_tuples):
    """get a random string from list of tuples (with weights)"""
    s = [t[0] for t in array_of_tuples]
    weights = [t[1] for t in array_of_tuples]
    sum_weights = sum(weights)
    weights_norm = [float(x) / sum_weights for x in weights]
    return str(np.random.choice(s, 1, p=weights_norm)[0])


def get_rnd_user_agent():
    """get a random user agent from list (with weights)"""
    # https://techblog.willshouse.com/2012/01/03/most-common-user-agents/
    user_agents = [
        ('Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36', 50),
        ('Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36', 40),
        ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36', 30),
        ('Mozilla/5.0 (Windows NT 6.1; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0', 45),
        ('Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36', 44),
        ('Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36', 41),
        ('Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36', 39),
        ('Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36', 36),
        ('Mozilla/5.0 (Windows NT 10.0; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0', 31),
        ('Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36', 25),
        ('Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko', 20),
        ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:45.0) Gecko/20100101', 19),
        ('Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36', 10),
        ('Mozilla/5.0 (Windows NT 6.3; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0', 5),
        ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586', 1),
    ]
    return get_rnd_from_tuple(user_agents)


def url2crc(url):
    return hashlib.md5(url.encode('utf-8')).hexdigest()


def find_parsers_sites(sites=None):
    modules_files = glob.glob(os.path.join("parsers", "*.py"))
    modules_names = {os.path.split(m)[1][:-3] for m in modules_files} - {"__init__"}
    if sites:
        modules_names = modules_names & set(sites)
        if modules_names != set(sites):
            raise ValueError('Sites not found: {}'.format(set(sites) - modules_names))
    return list(modules_names)


def load_parsers_sites(sites=None):
    return [importlib.import_module('parsers.'+m) for m in find_parsers_sites(sites)]


def prepare_params(site_config, parse_article_callback, feed_directory, log_directory, data_directory):
    site_params = site_config.copy()
    site_name = site_params['site']
    feed_directory = feed_directory.format(site=site_name, day=TODAY)
    log_directory = log_directory.format(site=site_name, day=TODAY)
    data_directory = data_directory.format(site=site_name, day=TODAY)
    site_params.update({
        'parse_article_callback': parse_article_callback,
        'log_file': '{dir}{site}.spider.log'.format(dir=log_directory, site=site_name),
        'feed_directory': feed_directory,
        'log_directory': log_directory,
        'data_directory': data_directory,
        'serialize_file_pattern': data_directory+'{}.html',
        'feed_format': 'jsonlines',
        'log_level': 'INFO',
        'delay': 0.90
    })
    return site_params


def read_feed(feed_url, site_params, run_args):
    feed_info = feedparser.parse(feed_url)

    if not feed_info:
        # nothing to process
        return None

    # ensure directories exists
    if not os.path.isdir(site_params['data_directory']):
        os.makedirs(site_params['data_directory'])
    if not os.path.isdir(site_params['log_directory']):
        os.makedirs(site_params['log_directory'])

    # init logger
    logger = logging.getLogger('rss_logger')
    logger_file_handler = logging.FileHandler(site_params['log_file'])
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    logger_file_handler.setFormatter(formatter)
    logger.addHandler(logger_file_handler)
    logger.setLevel(site_params['log_level'])
    logger.info('start process site {}'.format(site_params['site']))

    # load cache
    articles_cache = {}
    cache_filename = '{}articles.cache'.format(site_params['data_directory'])
    try:
        if os.path.isfile(cache_filename):
            with open(cache_filename, 'rb') as f:
                articles_cache = pickle.load(f)
    except:
        pass

    feed = {
        'url': feed_url,
        'feedinfo': feed_info,
        'articles': []
    }

    if run_args.verbose:
        print('process feed [{}]: {}'.format(site_params['site'], feed_url))

    # build list of urls to parse
    articles_in_error = []
    start_urls = []
    # for _i, feed_original in tqdm(enumerate(feed_info['entries'])):
    for i in tqdm(range(len(feed_info['entries'])), disable=not run_args.verbose):
        feed_original = feed_info['entries'][i]
        if not feed_original.link:
            continue
        url = site_params['regex_url_article_cleaner'].findall(feed_original.link)[0]
        if run_args.verbose:
            logger.info('process feed url: {}'.format(url))

        tmp_article_filename = site_params['serialize_file_pattern'].format(url2crc(url))
        need_download_article = True
        response_text = None
        if os.path.isfile(tmp_article_filename):
            # article has already been downloaded
            try:
                with open(tmp_article_filename, 'rb') as f:
                    article = pickle.load(f)
                    response_text = article['body_full']
                    need_download_article = \
                        feed_original[site_params['last_publish_update_field_name']] != article['feed_original'][site_params['last_publish_update_field_name']]
            except:
                articles_in_error.append(url)
                logger.exception('Error while parsing file {} from url {}'.format(tmp_article_filename, url))
                continue

        if need_download_article:
            # download article
            site_params['start_urls'] = start_urls
            site_params['run_args'] = run_args

            headers = {
                'user_agent': get_rnd_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'fr-FR,fr;q=0.8,en-US;q=0.6,en;q=0.4',
                'Accept-Encoding': 'gzip,deflate'
            }

            try:
                response = requests.get(url, headers=headers)
            except:
                articles_in_error.append(url)
                logger.exception('Error while downloading url {}'.format(url))
                continue
            sleep(site_params['delay'])
            if response.status_code != 200:
                continue
            if site_params.get('force_encoding'):
                response.encoding = site_params['force_encoding']
            response_text = response.text
            article = new_article(url, feed_original, body_full=response_text)

        # parse article
        try:
            success_article_parse, need_serialize = site_params['parse_article_callback'](article, response_text, logger)
        except Exception:
            need_serialize = True
            success_article_parse = False
            articles_in_error.append(url)
            if run_args.verbose:
                logger.exception('Error while parsing {}'.format(url))
            else:
                logger.error('Error while parsing {}'.format(url))

        # serialize article
        if need_serialize:
            with open(tmp_article_filename, 'wb') as f:
                pickle.dump(article, f)

        articles_cache[url] = {
            'last_date_parsed': datetime.datetime.utcnow(),
            'title': article.get('title', None),
            'success': success_article_parse
        }

        if success_article_parse:
            feed['articles'].append(article)

    # write cache articles
    with open(cache_filename, 'wb') as f:
        pickle.dump(articles_cache, f)

    # clean old articles
    # articles_to_delete = []
    # for url in articles_in_error:
    #     try:
    #         logger.error('article in error {}'.format(url))
    #         tmp_article_filename = site_params['serialize_file_pattern'].format(url2crc(url))
    #         with open(tmp_article_filename, 'rb') as f:
    #             article = pickle.load(f)
    #             if (datetime.datetime.utcnow() - article['download_date']).days > 30:
    #                 articles_to_delete.append(url)
    #         # TODO : delete old bad articles
    #     except:
    #         pass

    logger.info('end process site {}'.format(site_params['site']))
    logger.removeHandler(logger_file_handler)
    return feed


def run(run_args):
    """main function"""
    sites = load_parsers_sites(None if run_args.all else [run_args.website])
    for site_module in sites:
        site_params = prepare_params(site_module.config,
                                     site_module.parse_article,
                                     run_args.feeddir,
                                     run_args.logdir,
                                     run_args.datadir)
        feeds = []
        for feed_config in site_params['feeds']:
            feed_url = feed_config['url']
            try:
                feed = read_feed(feed_url, site_params, run_args)
                if feed:
                    str_xml_feed = build_feed(feed_config, feed['feedinfo'], feed['articles'])
                    # write cache articles
                    feed_filename = '{}{}'.format(site_params['feed_directory'], feed_config['name'])
                    if IS_PYTHON_3:
                        with open(feed_filename, 'wb') as f:
                            f.write(bytes(str_xml_feed, 'UTF-8'))
                        chmod(feed_filename, 0o644)
                    else:
                        with open(feed_filename, 'wb') as f:
                            f.write(str_xml_feed)
                        # chmod(feed_filename, 0o644)
                    feeds.append(feed)
            except Exception:
                logging.exception('Error while processing {}'.format(feed_url))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Web scraper')
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-f", "--feeddir", help="output feed directory", default=FEED_DIRECTORY)
    parser.add_argument("-o", "--datadir", help="output data directory", default=DATA_DIRECTORY)
    parser.add_argument("-l", "--logdir", help="output log directory", default=LOG_DIRECTORY)
    parser.add_argument("-w", "--website", help="web site name to scrap", default='')
    parser.add_argument("-u", "--usage", help="usage message", action="store_true")
    parser.add_argument("-a", "--all", help="all sites", action="store_true")
    args = parser.parse_args()
    if args.usage:
        print('usage example: -v -w "websitename"')
        print('list of sites:')
        for site in find_parsers_sites():
            print(site)
    else:
        run(args)
