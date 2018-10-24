#!/bin/sh
source /home/rss/rssenv/bin/activate
python spider_rss.py -w "bfmbusiness"
python spider_rss.py -w "developpez"
python spider_rss.py -w "lemonde"
python spider_rss.py -w "polygon"
python spider_rss.py -w "lesechos"
python spider_rss.py -w "lefigaro"
deactivate
