__author__ = 'bdavenport'

import json
import time
import urllib, urllib2
import yaml

# Attempt to load our configuration
try:
    f = open('config.yaml')
    config = yaml.load(f)
    f.close()
except IOError:
    config = {}

print config

#def pushData(data, url='http://adsb.mindlesstux.com/json/serverpush'):
def pushData(data, url='http://127.0.0.1:8080/json/serverpush'):
    try:
        x = urllib.urlencode(dict(messages=json.dumps(data)))
        request = urllib2.Request(url, x)
        request.add_header('User-agent', 'dumpHelper/0.1')
        if 'key' in config.keys():
            request.add_header('Client-Key', '%s' % (config['key']))
        response = urllib2.urlopen(request)
    except urllib2.URLError as e:
        print e.reason

#def pullData(url="http://127.0.0.1:8080"):
def pullData(url="http://raspberry.mindlesstux.com/dump1090/data.json"):
    response = urllib2.urlopen(url)
    x = response.read()
    print len(x)
    return x

# Perminate loop
while True:
    jsondata = pullData()
    pushData(jsondata)
    time.sleep(1)