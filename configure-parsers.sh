#!/bin/sh
SOURCE_DIR="/home/rss"
PARSERS_DIR="$SOURCE_DIR/parsers/"
ROOT_WWW_DIR="/var/www/rss/"
ROOT_DATA_DIR="/var/spiders/rss/data/"
ROOT_LOG_DIR="/var/log/spiders/rss/"
NGINX_CONFIG_FILE="$SOURCE_DIR/nginx-rss.conf"
# NGINX_DOMAIN="rss-news.top"
NGINX_DOMAIN="rss.rss-news.xyz"
BASH_SCRIPT_RUN_PARSERS="$SOURCE_DIR/run-parsers.sh"

valid_parser_files_concated=$(find $PARSERS_DIR -type f -name "*.py" | grep -v init | grep -v default)

# create directories
for filename in $valid_parser_files_concated;
do
    echo "now processing $filename"
    parser_name=$(echo $filename | rev | cut -d'.' -f2 | cut -d'/' -f1 | rev)
    echo "parser is: $parser_name"
    # create directories if not exists yet
    xml_feed_dir="$ROOT_WWW_DIR$parser_name/"
    data_dir="$ROOT_DATA_DIR$parser_name/"
    log_dir="$ROOT_LOG_DIR$parser_name/"
    mkdir -p $log_dir
    mkdir -p $xml_feed_dir
    mkdir -p $data_dir
done

# create nginx script
mkdir -p /var/log/nginx/rss/
echo "# nginx config file for rss feeds" > $NGINX_CONFIG_FILE
echo "# this config file has been generated by configure-parsers.sh" >> $NGINX_CONFIG_FILE
for filename in $valid_parser_files_concated;
do
    parser_name=$(echo $filename | rev | cut -d'.' -f2 | cut -d'/' -f1 | rev)
    echo "server {" >> $NGINX_CONFIG_FILE
    echo "    listen 80;" >> $NGINX_CONFIG_FILE
    echo "    # access_log off;" >> $NGINX_CONFIG_FILE
    echo "    server_name $parser_name.$NGINX_DOMAIN;" >> $NGINX_CONFIG_FILE
    echo "    access_log /var/log/nginx/rss/access_log;" >> $NGINX_CONFIG_FILE
    echo "    error_log /var/log/nginx/rss/error_log;" >> $NGINX_CONFIG_FILE
    echo "" >> $NGINX_CONFIG_FILE
    echo "    location / {" >> $NGINX_CONFIG_FILE
    echo "        root $ROOT_WWW_DIR$parser_name/;" >> $NGINX_CONFIG_FILE
    echo "        autoindex on;" >> $NGINX_CONFIG_FILE
    echo "        autoindex_localtime on;" >> $NGINX_CONFIG_FILE
    echo "        gzip on;" >> $NGINX_CONFIG_FILE
    echo "        gzip_vary on;" >> $NGINX_CONFIG_FILE
    echo "        gzip_min_length 1000;" >> $NGINX_CONFIG_FILE
    echo "        gzip_types text/plain text/xml application/xml application/json;" >> $NGINX_CONFIG_FILE
    echo "    }" >> $NGINX_CONFIG_FILE
    echo "}" >> $NGINX_CONFIG_FILE
    echo "" >> $NGINX_CONFIG_FILE
done

# create scipt to run all the parsers
echo "#!/bin/sh" > $BASH_SCRIPT_RUN_PARSERS
echo "source $SOURCE_DIR/rssenv/bin/activate" >> $BASH_SCRIPT_RUN_PARSERS
for filename in $valid_parser_files_concated;
do
    parser_name=$(echo $filename | rev | cut -d'.' -f2 | cut -d'/' -f1 | rev)
    echo "python spider_rss.py -w \"$parser_name\"" >> $BASH_SCRIPT_RUN_PARSERS
done
echo "deactivate" >> $BASH_SCRIPT_RUN_PARSERS
chmod u+x $BASH_SCRIPT_RUN_PARSERS
