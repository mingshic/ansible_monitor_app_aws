#!/usr/bin/python
# -*- coding: utf-8 -*-
# -- author: hanyn@easemob.com --


import sys
import requests
import re

if len(sys.argv) != 2:
    print "Usage: script dashboard_ip"
    sys.exit()

dashboard_ip = sys.argv[1]

url="http://"+dashboard_ip+":18087/api/overview"
apidata = requests.get(url)
content = apidata.content
items = re.findall('"ops": \d+', content)
ops = items[0].split(":")[1].strip()

print(ops)
