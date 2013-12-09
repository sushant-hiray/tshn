#!/bin/sh
python /home/sushant/code/tshn/scrape.py --get >> /home/sushant/code/tshn/scrape.log
python /home/sushant/code/tshn/scrape.py --process >> /home/sushant/code/tshn/scrape.log
python /home/sushant/code/tshn/scrape.py --combine >> /home/sushant/code/tshn/scrape.log
