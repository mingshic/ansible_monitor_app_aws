#!/usr/bin/env python
#coding:utf-8
import os
import json

port_list=[]
port_dict={"data":None}
easemob_port={
    "8080": "tomcat",
    "3000": "grafana",
    "80": "nginx",
    "3306": "mysql",
    "9160":"cassandra",
    "6996": "conference",
    "2181":"zk"
    }
easemob_port_keys=easemob_port.keys()
cmd='''/usr/sbin/ss -lnt|grep "^LISTEN"|awk '{print $4}'|awk -F":" '{if ($NF~/^[0-9]*$/) print $NF}'|sort |uniq  2>/dev/null'''
local_ports=os.popen(cmd).readlines()
for port in local_ports:
    port=port.replace("\n", "")
    if port in easemob_port_keys:
        pdict={}
        pdict["{#TCP_PORT}"]=port
        pdict["{#PORT_DESC}"]=easemob_port[port]
        port_list.append(pdict)
port_dict["data"]=port_list
#print port_dict
jsonStr = json.dumps(port_dict, sort_keys=True, indent=4)
print jsonStr

