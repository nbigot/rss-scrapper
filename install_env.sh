#!/bin/sh
# create a python virtual env for rss feed generate execution
cd /home/rss
pip install virtualenv
virtualenv -p python3.4 rssenv
source rssenv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
