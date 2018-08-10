#!/usr/bin/env python
#coding:utf-8

import json
import urllib2
from urllib2 import HTTPError, URLError

url = "http://172.16.90.130/zabbix/api_jsonrpc.php"
header = {"Content-Type":"application/json"}

def auth():
	data = json.dumps({
		"jsonrpc": "2.0",
		"method": "user.login",
		"params": {
		"user": "Admin",
		"password": "zabbix"
		},
		"id": 100
	})
	Request = urllib2.Request(url,data)
	for key in header:
		Request.add_header(key,header[key])
	try:
		result = urllib2.urlopen(Request)
	except (HTTPError,URLError) as e:
		print 'Url Error %s' % e
	else:
		Response = json.loads(result.read())
		if 'error' in Response:
			print 'Login failed'
		else:
			return Response['result']

def getdata(url,data):
	Request = urllib2.Request(url,data)
	for key in header:
		Request.add_header(key,header[key])
	result = urllib2.urlopen(Request)
	Response = json.loads(result.read())
	return Response	


def getHost():
	data = json.dumps({
	        "jsonrpc": "2.0",
	        "method": "host.get",
	        "params": {
	                "output": "extend",
	                "filter": {
	                    "host": ["{{ agenthostname }}"]
	          }
	        },
	        "auth": auth(),
	        "id": 101
	        })
	hostresponses = getdata(url,data)
	if len(hostresponses['result']) == 0:
		return None
	else:
		print hostresponses['result']
		return hostresponses['result'][0]['host']
def getGroupID():
	data = json.dumps({
		"jsonrpc": "2.0",
    		"method": "hostgroup.get",
    		"params": {
        		"output": "extend",
        		"filter": {
        		    "name": ["{{ zabbixgroup }}"]
        		}
    		},
    		"auth": auth(),
    		"id": 102
		})
	groupidrespones = getdata(url,data)
    	return groupidrespones['result'][0]['groupid']

def addHost():
	data = json.dumps({
		"jsonrpc": "2.0",
		"method": "host.create",
		"params": {
      			"host": "{{ agenthostname }}",
        		"interfaces": [
        			{
                			"type": 1,
                			"main": 1,
                			"useip": 1,
                			"ip": "{{ agentIP }}",
                			"dns": "",
                			"port": "10050"
        			}
        		],
        		"groups": [
        			{
                			"groupid": getGroupID()
        			}
        		],

    		},
    		"auth": auth(),
    		"id": 103
    	})
	if getHost() is None:
		addhostresponses = getdata(url,data)
                return addhostresponses
	else:
		print "Host monitor-server has been existdd!"
	

if __name__ == '__main__':
	addHost()
