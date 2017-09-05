# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup, NavigableString
from sys import version_info
from html import escape
import re


config = {
    'site': 'lefigaro',
    'websitename': 'lefigaro',
    'feeds': [
        {
            'url': 'http://www.lefigaro.fr/rss/figaro_actualites.xml',
            'name': 'rss_une_titres.xml',
            'icon': 'http://a.f1g.fr/f/img/favicon/favicon-32x32.png?v20170831115844',
            'logo': '',
        },
    ],
    'allowed_domains': ['lefigaro.fr'],
    'regex_url_article_cleaner': re.compile('(?P<url>.*)'),
    'last_publish_update_field_name': 'updated'
}


def parse_article(article, response_text, logger):
    parsed_succeed = True
    last_parsed_succeed = article.get('last_parsed_succeed', None)
    article['article_format'] = None
    soup = BeautifulSoup(response_text, 'html.parser')
    try:
        article['date_modified'] = article['feed_original'].get('updated')
    except:
        pass
    try:
        content_html = u''
        article_body = soup.findAll(attrs={"itemprop": "articleBody"})[0]
        for elem in article_body:
            if elem.name in ['h1', 'h2', 'h3']:
                content_html += u'&lt;h2&gt;' + escape(elem.text.strip()) + u'&lt;/h2&gt;'
            elif elem.name == 'p' and 'lire' not in elem.attrs.get('class', []):
                content_html += u'&lt;p&gt;' + escape(elem.text.strip()) + u'&lt;/p&gt;'
        article['content_html'] = content_html
        article['article_format'] = 1
    except:
        parsed_succeed = False
    need_serialize = not last_parsed_succeed or not parsed_succeed
    article['last_parsed_succeed'] = last_parsed_succeed
    if not parsed_succeed:
        return False, need_serialize
    published = article['feed_original'].get('updated', '')
    if version_info < (3, 0):
        published = unicode(published)
    try:
        enclosure = next((link for link in article['feed_original']['links'] if link['rel'] == 'enclosure'), {})
    except:
        enclosure = {}
    article['rss'] = {
        'published': published,
        'updated': article.get('date_modified', ''),
        'title': article['feed_original']['title'],
        'link': article['feed_original'].get('link', article['url']),
        'id': article['feed_original'].get('guid', article['url']),
        'author': article['feed_original'].get('author', ''),
        'content_html': article['content_html'],
        'enclosure_type': enclosure.get('type', ''),
        'enclosure_href': enclosure.get('href', ''),
        'enclosure_length': enclosure.get('length', ''),
    }
    return parsed_succeed, need_serialize
