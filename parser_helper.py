# -*- coding: utf-8 -*-

from datetime import datetime


def response_extract(selector, expr, index=0, join_str=None, strip=True, default=None, cast_as_int=False):
    """ helper extract text from response selector (lib parsel)"""
    r = selector.css(expr).extract()
    if r is None or len(r) <= index:
        return default
    else:
        if join_str:
            r2 = join_str.join(r)
        else:
            r2 = r[index]
        if strip:
            r2 = r2.strip()
        if cast_as_int:
            try:
                r2 = int(r2)
            except:
                return default
        return r2


def new_article(url, feed_original, body_full=None):
    return {
        'url': url,
        'date_published': None,
        'date_modified': None,
        'author': None,
        'title': None,
        'feed': None,
        'feed_original': feed_original,
        'body_full': body_full,
        'body_article': None,
        'chapeau_article': None,
        'download_date': datetime.utcnow()
    }


def build_feed(feed_config, feed_def, articles):

    feed_template = u"""<?xml version="1.0" encoding="UTF-8"?>
    <feed xmlns="http://www.w3.org/2005/Atom" xml:lang="{feed_lang}">
        <title>{feed_title}</title>
        <subtitle>{feed_subtitle}</subtitle>
        <icon>{feed_icon}</icon>
        <logo>{feed_logo}</logo>
        <updated>{feed_updated}</updated>
        <id>{feed_id}</id>
        <link type="text/html" href="{feed_alternate}" rel="alternate"/>
        {feed_articles}
    </feed>"""

    article_template = u"""        <entry>
            <published>{published}</published>
            <updated>{updated}</updated>
            <title>{title}</title>
            <link rel="alternate" type="text/html" href="{link}"/>
            <id>{id}</id>
            <author>
                <name>{author}</name>
            </author>
            <content type="html">
                {content_html}
            </content>
        </entry>"""

    if articles:
        if len(articles) == 1:
            feed_articles = articles[0]
        else:
            feed_articles = u"\n".join([article_template.format(**article['rss']) for article in articles])
    else:
        feed_articles = u''

    f = feed_def['feed']
    feed_render = feed_template.format(
        feed_title=f['title'],
        feed_subtitle=f.get('subtitle', ''),
        feed_lang=f.get('lang', f.get('language', 'en-US')),
        feed_icon=feed_config.get('icon', ''),
        feed_logo=feed_config.get('logo', ''),
        feed_updated=f.get('updated', ''),
        feed_id=feed_def['href'],
        feed_alternate=f.get('alternate', ''),
        feed_articles=feed_articles
    )

    # remove empty fields if any
    feed_render = feed_render.replace('<subtitle></subtitle>', '')
    feed_render = feed_render.replace('<icon></icon>', '')
    feed_render = feed_render.replace('<logo></logo>', '')
    feed_render = feed_render.replace('<link type="text/html" href="" rel="alternate"/>', '')

    return feed_render
