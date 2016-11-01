#!/bin/sh
source /home/rss/rssenv/bin/activate
python spider_rss.py -w "${1}"
deactivate
