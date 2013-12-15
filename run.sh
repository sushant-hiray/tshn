#!/bin/sh
python /var/www/tshn/scrape.py --get > /var/www/tshn/scrape.log
python /var/www/tshn/scrape.py --process >> /var/www/tshn/scrape.log
python /var/www/tshn/scrape.py --combine >> /var/www/tshn/scrape.log
python /var/www/tshn/scrape.py --clean >> /var/www/tshn/scrape.log