# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from sys import version_info
from html import escape
import re


config = {
    'site': 'polygon',
    'websitename': 'polygon',
    'feeds': [
        {
            'url': 'http://www.polygon.com/rss/group/news/index.xml',
            'name': 'rss_polygon.xml',
            'icon': '',
            'logo': '',
        },
    ],
    'allowed_domains': ['polygon.com'],
    'regex_url_article_cleaner': re.compile('(?P<url>.*)'),
    'last_publish_update_field_name': 'updated'
}


def parse_article(article, response_text, logger):
    parsed_succeed = True
    last_parsed_succeed = article.get('last_parsed_succeed', None)
    article['article_format'] = None
    try:
        article['date_modified'] = article['feed_original'].get('updated')
    except:
        pass
    try:
        content_html = u''
        soup = BeautifulSoup(response_text, 'html.parser')
        article_body = soup.find("div", {"class": "c-entry-content"})
        for p in article_body.find_all('p'):
            content_html += u'&lt;p&gt;' + escape(p.text) + u'&lt;/p&gt;'
        article['content_html'] = content_html
        article['article_format'] = 1
    except:
        parsed_succeed = False
    need_serialize = not last_parsed_succeed or not parsed_succeed
    article['last_parsed_succeed'] = last_parsed_succeed
    if not parsed_succeed:
        return False, need_serialize
    try:
        published = article['feed_original'].get('updated', '')
        article['date_published'] = published
        if version_info < (3, 0):
            published = unicode(published)
    except:
        pass
    try:
        enclosure = next((link for link in article['feed_original']['links'] if link['rel'] == 'enclosure'), {})
    except:
        enclosure = {}
    article['rss'] = {
        'published': published,
        'updated': article.get('date_modified', ''),
        'title': article['feed_original']['title'],
        'link': article['feed_original'].get('link', article['url']),
        'id': article['feed_original'].get('id', article['url']),
        'author': article['feed_original'].get('author', ''),
        'content_html': article['content_html'],
        'enclosure_type': enclosure.get('type', ''),
        'enclosure_href': enclosure.get('href', ''),
        'enclosure_length': enclosure.get('length', ''),
    }
    return parsed_succeed, True
