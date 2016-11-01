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
    'site': 'lesechos',
    'websitename': 'les-echos',
    'feeds': [
        {
            'url': 'http://syndication.lesechos.fr/rss/rss_une_titres.xml',
            'name': 'rss_une_titres.xml',
            'icon': 'http://lesechos.rss.domisiladore.com/favicon.ico',
            'logo': '',
        },
        {
            'url': 'http://www.lesechos.fr/rss/rss_articles_journal.xml',
            'name': 'rss_articles_journal.xml',
            'icon': 'http://lesechos.rss.domisiladore.com/favicon.ico',
            'logo': '',
        },
        {
            'url': 'http://syndication.lesechos.fr/rss/rss_plus_consultes.xml',
            'name': 'rss_plus_consultes.xml',
            'icon': 'http://lesechos.rss.domisiladore.com/favicon.ico',
            'logo': '',
        },
    ],
    'allowed_domains': ['lesechos.fr'],
    'regex_url_article_cleaner': re.compile('(?P<url>.+?)(?=#)'),
    'force_encoding': 'utf-8',
    'last_publish_update_field_name': 'published_parsed'
}


def parse_article(article, response_text, logger):
    """parse inner article"""
    sel = Selector(text=response_text)
    parsed_succeed = True
    last_parsed_succeed = article.get('last_parsed_succeed', None)
    try:
        article['date_published'] = response_extract(sel, 'time[itemprop=datePublished]::attr(datetime)')
        if not article['date_published']:
            article['date_published'] = response_extract(sel, 'meta[property="article:published_time"]::attr(content)')
    except:
        article['date_published'] = article['feed_original']['published_parsed']
        pass
    try:
        article['date_modified'] = response_extract(sel, 'time[itemprop=dateModified]::attr(datetime)')
        if not article['date_modified']:
            article['date_modified'] = response_extract(sel, 'meta[property="article:modified_time"]::attr(content)')
    except:
        article['date_modified'] = None
        pass
    try:
        article['author'] = response_extract(sel, '.meta-author span::text')
        if not article['author']:
            article['author'] = response_extract(sel, 'meta[itemprop=creator]::attr(content)')
        if not article['author']:
            article['author'] = response_extract(sel, 'meta[property="article:author"]::attr(content)')
    except:
        pass
    try:
        if sel.css('h1.title-article span::text').extract():
            title_part1 = response_extract(sel, 'h1.title-article span::text')
            title_part2 = response_extract(sel, 'h1.title-article::text', index=1)
            article['title'] = title_part1 + title_part2
        else:
            article['title'] = response_extract(sel, 'h1.title-article::text', join_str=' ')
        if not article['title']:
            article['title'] = response_extract(sel, 'title::text')
    except:
        pass
    article['article_format'] = None
    content_article = sel.css('.content-article')
    if content_article:
        article['chapeau_article'] = response_extract(content_article, 'h2.chapo-article::text', join_str=' ')
        article['broken_html'] = content_article.extract_first()
        content_html = u''
        soup = BeautifulSoup(article['broken_html'], 'html.parser')
        article_body = soup.findAll(attrs={"itemprop": "articleBody"})
        for elem in article_body:
            if elem.name in ['h1', 'h2', 'h3']:
                content_html += u'&lt;h2&gt;' + escape(elem.text.strip()) + u'&lt;/h2&gt;'
            elif elem.name == 'p':
                content_html += u'&lt;p&gt;' + escape(elem.text.strip()) + u'&lt;/p&gt;'
        article['content_html'] = content_html
        article['article_format'] = 1
    else:
        # try another format
        article['chapeau_article'] = response_extract(sel, 'h2.chapeau-article::text', join_str=' ')
        content_article = sel.css('div.contenu_article')
        if content_article:
            article['broken_html'] = content_article.extract_first()
            content_html = u''
            soup = BeautifulSoup(article['broken_html'], 'html.parser')
            article_body = soup.findAll(attrs={"itemprop": "articleBody"})[0]
            for elem in article_body:
                if elem.name in ['h1', 'h2', 'h3']:
                    content_html += u'&lt;h2&gt;' + escape(elem.text.strip()) + u'&lt;/h2&gt;'
                elif elem.name == 'p':
                    content_html += u'&lt;p&gt;' + escape(elem.text.strip()) + u'&lt;/p&gt;'
            article['content_html'] = content_html
            article['article_format'] = 2
        else:
            parsed_succeed = False
            pass

    need_serialize = not last_parsed_succeed or not parsed_succeed
    article['last_parsed_succeed'] = parsed_succeed

    if not parsed_succeed:
        return False, need_serialize

    published = datetime.fromtimestamp(mktime(article['feed_original']['published_parsed'])).isoformat()
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
        'link': article['feed_original']['link'],
        'id': article['feed_original']['link'],
        'author': article['feed_original']['author'],
        'content_html': article['content_html'],
        'enclosure_type': enclosure.get('type', ''),
        'enclosure_href': enclosure.get('href', ''),
        'enclosure_length': enclosure.get('length', ''),
    }

    return True, need_serialize
