#!/bin/sh
# configure nginx for rss feed
ln -s /home/rss/nginx-rss.conf /etc/nginx/conf.d/
systemctl restart nginx
