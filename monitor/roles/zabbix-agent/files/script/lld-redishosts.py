#!/usr/bin/python

import json
import subprocess

if __name__ == '__main__':
#    process = subprocess.Popen("cat /proc/diskstats | awk '{print $3}' | grep -v 'ram\|loop\|sr\|dm'", shell=True, stdout=subprocess.PIPE)
    process = subprocess.Popen("cat /tmp/redisdashboardlist | grep -E 'Server'|awk '{print $2}' 2>/dev/null", shell=True, stdout=subprocess.PIPE)
#    process = subprocess.Popen("cat /tmp/redisdashboardlist | grep -E 'Server'|awk '{print $2}'|sed 's/:/_/g' 2>/dev/null", shell=True, stdout=subprocess.PIPE)
    output = process.communicate()[0]
    data = list()
    for line in output.split("\n"):
        if line:
            data.append({"{#DEVICE}": line})

    print(json.dumps({"data": data}, indent=4))
