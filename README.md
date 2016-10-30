# RSS Scrapper

## What is RSS Scrapper?

RSS Scrapper goal is to produce better/richer rss feeds than originals.

It loads and replaces content of an original article by an article loaded from the refered web site.
Then it create one or multiples xml files for each site.
You can host those produced xml files with a web server to serve them as static (auto-updated) content by using nginx for example.
Finally use your favorite rss reader to read them.

## Getting started

### Requirements

You need python 3.x (it may work with python 2.7 but no garanties for that).

### Installation

Download all the files from this repository.

Copy them into your installation directory, for example */home/rss/*

Run configuration script:

```bash
$ sudo /home/rss/configure-parsers.sh
$ cp /home/rss/nginx-rss.conf /etc/nginx/conf.d/nginx-rss.conf
$ sudo systemctl restart nginx
```

#### Summary list of directories to look at:

| **What**          | **Directory**                        |
|-------------------|--------------------------------------|
|source code        |_/home/rss/_                          |
|sites parsers      |_/home/rss/parsers/_                  |
|produced xml feeds |_/var/www/rss/yoursitename/_          |
|intermediate datas |_/var/spiders/rss/data/yoursitename/_ |
|log files          |_/var/log/spiders/rss/yoursitename/_  |


#### Run in production

Note: For a technical reason having a dedicated sub-domain name for each site is mandatory if we want to have a different  _favicon.ico_ for each site.
By a domain name then create a sub-domain DNS redirection for each site/parser to target the same server ip.
If you don't want to by a domain name you will have to modify the script _configure-parsers.sh_ so that it produces a different configuration file for nginx.


##### Setup Auto rotate log files

```bash
$ sudo cp /home/rss/logrotate-rss.conf /etc/logrotate.d/rss
```

##### Setup Update your rss feeds

Auto update your rss feeds

```bash
$ crontab -e
```
Execute every 20 minutes betwin hours 07 and 23 every day.
```
*/20 7-23 * * * /home/rss/run-all.sh
```

##### Checklist for running in producion

  - Configuration script has been runned
  - Directories are created for each parser
    - output xml directory
    - intermediate data directory
    - output log directory
  - Nginx
    - configuration file is ok
    - nginx server has been restarted
  - Logrotate configuration file is ok
  - Crontab has been set

##### Troubleshooting

Check log files

  - Check xml files are there in _/var/www/rss/*/\*.xml_
  - Check your nginx log files in 
    - _/var/log/nginx/rss/error_log_
    - _/var/log/nginx/rss/access_log_
  - Check localhost emails (if any error while running process from crontab)

#### Run standalone
Be shure your python version is >= 3.x
```bash
$ source /home/rss/rssenv/bin/activate
$ /home/rss/spider_rss.py -v -w "myparsername"
$ deactivate
```

## Write your own parsers

Simply create a new python file in the _parsers_ directory by copying an existing one and rename it.
Then edit the new file to configure it and write your python code.
```bash
$ cp /home/rss/parsers/default.py /home/rss/parsers/mynewparser.py
$ vi /home/rss/parsers/mynewparser.py
...
```

Warning: the name of the parser file IS the same as the name of your sub-domain

Don't forget to create directories :
```bash
$ mkdir -p /var/www/rss/mynewparser/
$ mkdir -p /var/spiders/rss/data/mynewparser/
$ mkdir -p /var/log/spiders/rss/mynewparser/
```

Then run your parser:
```bash
$ /home/rss/spider_rss.py -v -w "myparsername"
```

Then Check the produced output xml file:
```bash
$ cat /var/www/rss/mynewparser/*.xml
```

When you're happy with your parser, put it into production:
```bash
$ sudo /home/rss/configure-parsers.sh
$ sudo systemctl restart nginx
```


## License

MIT
