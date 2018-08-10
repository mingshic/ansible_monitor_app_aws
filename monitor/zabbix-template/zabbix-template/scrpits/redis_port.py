#!/usr/bin/env python
#coding: utf-8
import os
import json
t=os.popen("""sudo netstat -natp 2>/dev/null |awk -F: '/redis-server|codis-server/&&/LISTEN/{print $2}'|awk '{print $1}' """)
ports = []
for port in  t.readlines():
        r = os.path.basename(port.strip())
        ports += [{'{#REDISPORT}':r}]
print json.dumps({'data':ports},sort_keys=True,indent=4,separators=(',',':'))
