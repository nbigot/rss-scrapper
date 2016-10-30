# -*- coding: utf-8 -*-

from parser_helper import response_extract
from parsel import Selector
from bs4 import BeautifulSoup
from time import mktime
from datetime import datetime
from sys import version_info
from html import escape
import re


config = {
    'site': 'CHANGETHIS',
    'websitename': 'CHANGETHIS',
    'feeds': [
        {
            'url': 'http://CHANGETHIS.com/CHANGETHIS.xml',
            'name': 'rss_CHANGETHIS.xml',
            'icon': 'http://CHANGETHIS/favicon.ico',
            'logo': '',
        },
    ],
    'allowed_domains': ['CHANGETHIS.com'],
    'regex_url_article_cleaner': re.compile('(?P<url>.+?)(?=#)'),
}


def parse_article(article, response_text, logger):
    if 'feed_original' not in article:
        return False
    article['feed'] = article['feed_original']
    return True, True
