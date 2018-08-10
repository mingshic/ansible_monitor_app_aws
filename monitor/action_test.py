#!/usr/bin/env python
#coding:utf-8

import json
import urllib2
from urllib2 import HTTPError, URLError

url = "http://172.18.201.51:88/zabbix/api_jsonrpc.php"
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


def action_exists():
        data = json.dumps({
		"jsonrpc": "2.0",
        	"method": "action.exists",
        	"params": {
        		"name": "vpn1"
    		},
    		"auth": auth(),
    		"id": 1
	})
	actionexists = getdata(url,data)
        print actionexists

def action_get():
	data = json.dumps({
		"jsonrpc": "2.0",    
		"method": "action.get",
		"params": {
		#	"actionid": 7,
        		"output": "extend",
        		"selectOperations": "extend",
        		"selectConditions": "extend",
        		"filter": {
            			"eventsource": 1
        		}
    		},	
    		"auth": auth(),
	    	"id": 101
	})
	actiontest = getdata(url,data)
	print actiontest

if __name__ == '__main__':
	action_get()
