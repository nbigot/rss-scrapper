#!/bin/sh
source /home/rss/rssenv/bin/activate
python spider_rss.py -w "developpez"
python spider_rss.py -w "lesechos"
python spider_rss.py -w "polygon"
deactivate
