#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python /home/pi/Yaha/http_test.py


import urllib2
import urllib
 
query_args = {}
 
url = 'http://10.0.0.91/livedata.htm'
 
data = urllib.urlencode(query_args)
 
request = urllib2.Request(url, data)
 
response = urllib2.urlopen(request).read()
 
print response