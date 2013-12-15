from optparse import OptionParser
import json
import re
import os,errno
import shutil
from datetime import datetime, timedelta
import time
import urllib
from bs4 import BeautifulSoup

# python scrape.py --get scrapes the first page of HN
# python scrape.py --process --combine --upload
# python scrape.py --deploy

# Set up Regexes
RE_NUM = re.compile(r'\d+')
RE_TIME_AGO = re.compile(r'\d+\s\w+?\sago')

#silently remove a file
def silentremove(filename):
    try:
        os.remove(filename)
    except OSError as e: # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
            raise # re-raise exception if a different error occured
# Download the first page of HN
def get(filename):
    f = open(filename,'w')
    url = 'http://news.ycombinator.com/news'
    r=urllib.urlopen(url)
    if r.getcode() == 200:
        f.write(r.read())
        f.close()
        print "Wrote the data into file " + filename
    else:
        print "Could not get HN feed"
        print "Status code is:" + r.getcode()
        exit()

# Extract info from the HTML
def process(infile, outfile):
    f = open(infile,'r')
    soup = BeautifulSoup(f.read())
    summary = []

    now = time.time()
    print 'Current epoch time: %d' % int(now)

    #[2:] because first matches with a login thingy
    for row in soup.find_all('tr')[2:]:
        if len(row.find_all('td')) == 3:
            cells = row.find_all('td')
            info_row = row.next_sibling
            order = cells[0].text
            link_data = cells[2]
            title = cells[2].find('a').text
            url = cells[2].find('a')['href']
            domain = cells[2].find('span').text if cells[2].find('span') else ''
            points = info_row.find('span').text if info_row.find('span') else ''
            user = info_row.find('a').text if info_row.find('a') else ''
            num_comments = info_row.find_all('a')[1].text if len(info_row.find_all('a')) > 1 else ''
            thread_id = info_row.find_all('a')[1]['href'] if len(info_row.find_all('a')) > 1 else ''
            time_ago_str = RE_TIME_AGO.search(info_row.text).group(0)
            num, time_type, other = time_ago_str.split(' ')
            if 'minute' in time_type:
                posted = now - int(num) * 60
            elif 'hour' in time_type:
                posted = now - int(num) * 60 * 60
            elif 'day' in time_type:
                posted = now - int(num) * 60 * 60 * 24
            else:
                print 'Error processing time ago string: %s' % time_ago_str
                exit()

            thread_type = 'Jobs' if thread_id == '' else 'Other'

            data = {'order' : RE_NUM.search(order).group(0),
                    'title' : title,
                    'url'   : url,
                    'domain': domain.strip('() '),
                    'points': int(RE_NUM.search(points).group(0)) if 'point' in points else 0,
                    'user'  : user,
                    'num_comments' : int(RE_NUM.search(num_comments).group(0)) if 'comments' in num_comments else 0,
                    'thread_id' : RE_NUM.search(thread_id).group(0) if 'item' in thread_id else '',
                    'type' : thread_type,
                    'posted_time' : int(posted),
                    }
            summary.append(data)
    f.close()

    print json.dumps(summary, indent=2)

    o = open(outfile,'w')
    o.write(json.dumps(summary, indent=2))
    o.close()

# Combine the recent files into a big file of data
def combine(now):
    recent_24 = now - timedelta(hours=24)
    # Combine files
    current_data = []
    datetime_cnt = recent_24
    while datetime_cnt <= now:
        print 'Processing data for %s?' % datetime_cnt.strftime('%Y-%m-%d-%H-%M'),
        fn = 'hn-data-%s.json' % datetime_cnt.strftime('%Y-%m-%d-%H-%M')
	fp="/var/www/tshn/"
        fp += os.path.join('data', fn)
        if os.path.exists(fp):
            print 'Y'
            f = open( fp, 'r')
            current_data.extend(json.loads(f.read()))
            f.close()
        else:
            print 'N'
        datetime_cnt += timedelta(minutes=15)

    print 'Got %d rows' % len(current_data)
    fp="/var/www/tshn/"
    fp+=os.path.join('data','now.json')
    f = open(fp,'w')
    f.write(json.dumps(current_data,indent=2))
    f.close()

    # Save this snapshot if it's midnight so we have a daily history
    if now.hour == 0 and now.minute == 0:
        fn = 'hn-data-%s.json' % now.strftime('%Y-%m-%d')
        shutil.copyfile(os.path.join('data', 'now.json'), os.path.join('data', fn))

#clean previous day's counterpart file
def clean(now):
    past=datetime.now()-timedelta(days=1)
    past = past.replace(minute=(past.minute/15)*15)
    filename = "/var/www/tshn"
    filename =  filename + "/" + os.path.join('data','hn-data-%s.html' % past.strftime('%Y-%m-%d-%H-%M'))
    filename_json = filename.replace('.html','.json')
    silentremove(filename)
    silentremove(filename_json)


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-a", "--all", action="store_true", dest="all", default=None, help="Run the entire script")
    parser.add_option("-g", "--get", action="store_true", dest="get", default=None, help="Get most recent data")
    parser.add_option("-p", "--process", action="store_true", dest="process", default=None, help="Process most recent data")
    parser.add_option("-c", "--combine", action="store_true", dest="combine", default=None, help="Combine recent data files")
    parser.add_option("-d", "--clean", action="store_true", dest="clean", default=None, help="Clean previous days data files")
    (options, args) = parser.parse_args()

    if options.all:
        options.get = options.process = options.combine = True

    now = datetime.now()
    now_15 = now.replace(minute=(now.minute/15)*15)
    filename = "/var/www/tshn"
    filename =  filename + "/" + os.path.join('data','hn-data-%s.html' % now_15.strftime('%Y-%m-%d-%H-%M'))
    filename_js = filename.replace('.html','.json')

    if options.get:
        print 'Getting HN data'
        get(filename)

    if options.process:
        print 'Processing HN data'
        process(filename, filename_js)

    if options.combine:
        print 'Generating a data file'
        combine(now_15)

    if options.clean:
        print 'Removing previous data files'
        clean(now_15)
