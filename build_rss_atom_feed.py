# -*- coding: utf-8 -*-
from parser_helper import build_feed


if __name__ == "__main__":
    # example: http://www.polygon.com/rss/index.xml
    feed_config = {
        'icon': 'https://cdn3.vox-cdn.com/community_logos/42931/favicon.ico',
        'logo': ''
    }

    feed_def = {
        'href': 'http://www.polygon.com/rss/group/news/index.xml',
        'feed': {
            'title': 'Polygon - News',
            'lang': 'en',
            'updated': '2016-08-30T16:00:03-04:00',
            'url': 'http://www.polygon.com/rss/group/news/index.xml',
            'alternate': 'http://www.polygon.com/news'
        }
    }

    articles = [
        {
            'rss': {
                'published': '2016-08-30T14:30:02-04:00',
                'updated': '2016-08-30T14:30:02-04:00',
                'title': 'Halo’s Warthog drifting into Forza Horizon 3',
                'link': 'http://www.polygon.com/2016/8/30/12712342/playable-halo-warthog-forza-horizon-3',
                'id': 'http://www.polygon.com/2016/8/30/12712342/playable-halo-warthog-forza-horizon-3',
                'author': 'Thomas Biery',
                'content_html': 'This is a text'
            }
        },
        {
            'rss': {
                'published': '2016-08-30T14:30:02-04:00',
                'updated': '2016-08-30T14:30:02-04:00',
                'title': 'Halo’s Warthog drifting into Forza Horizon 3',
                'link': 'http://www.polygon.com/2016/8/30/12712342/playable-halo-warthog-forza-horizon-3',
                'id': 'http://www.polygon.com/2016/8/30/12712342/playable-halo-warthog-forza-horizon-3',
                'author': 'Thomas Biery123',
                'content_html': 'This is another text'
            }
        },
    ]
    feed = build_feed(feed_config, feed_def, articles)
    print(feed)
