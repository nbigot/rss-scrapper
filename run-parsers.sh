#!/bin/sh
source /home/rss/rssenv/bin/activate
python spider_rss_v2.py -w "developpez"
python spider_rss_v2.py -w "lesechos"
python spider_rss_v2.py -w "polygon"
deactivate
