#!/bin/sh
find /var/spiders/rss/data/* -mtime +15 -type f -delete
cd /home/rss
/home/rss/run-parsers.sh
