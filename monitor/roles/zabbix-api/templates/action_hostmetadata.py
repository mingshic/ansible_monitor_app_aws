#!/usr/bin/env python
#coding:utf-8

import json
import urllib2
from urllib2 import HTTPError, URLError

url = "http://{{ zabbix_IP_daemon }}/zabbix/api_jsonrpc.php"
header = {"Content-Type":"application/json"}

def auth():
	data = json.dumps({
		"jsonrpc": "2.0",
		"method": "user.login",
		"params": {
		"user": "{{ zabbix_authori_user }}",
		"password": "{{ zabbix_authori_password }}"
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


def action_get():
	data = json.dumps({
   		"jsonrpc": "2.0",
   		"method": "action.get",
   		"params": {
 	   		"output": "extend",
   	        	"selectOperations": "extend",
   	       		"selectRecoveryOperations": "extend",
   	        	"selectFilter": "extend",
   	        	"filter": {
   	        	    	"eventsource": 2
   	        	}
   	    	},
   	    	"auth": auth(), 
   	    	"id": 105
   	})
	actiongetreponse = getdata(url,data)
	print actiongetreponse 

def action_group():
	data = json.dumps({
	        "jsonrpc": "2.0",
	        "method": "action.create",
	        "params": {
                        "name": "{{ action_name }}",
			"status": 0,
			"def_shortdata": "Auto registration: {HOST.HOST}",
			"def_longdata": "Host name: {HOST.HOST}\r\nHost IP: {HOST.IP}\r\nAgent port: {HOST.PORT}",
			"esc_period": 0,
			"eventsource": 2,
			"filter": {
				"evaltype": 0,
				"conditions": [
					{
						"conditiontype": 24,
						"value": "{{ condition_name_value }}",
				#		"value2": "",
				#		"formulaid": "A",
						"operator": 2,
					}
				],
			},
			"operations": [
				{
					"operationtype": 4,
		#			"esc_period": 0,
		#			"esc_step_from": "1",
                #  			"esc_step_to": "1",
		#			"evaltype": 0,
		#			"opconditions": [],
		#			"recovery": 0,
					"opgroup": [
						{
							"groupid": getGroupID(),
						}
					]
				},
                                {
                                        "operationtype": 6,
                                        "optemplate": [
                                                {
                                                        "templateid": getTemplateID(),
                                                }
                                        ]
                                }
			]
		},
	        "auth": auth(),
	       	"id": 101
        })
	actionresponses = getdata(url,data)
	if "error" in actionresponses:
                print "vpn2 is exist!"

def createGroup():
	data = json.dumps({
		"jsonrpc": "2.0",
		"method": "hostgroup.create",
		"params": {
			"name": "{{ group_name }}"
		},
		"auth": auth(),
		"id": 102
	})
	createGroupdata = getdata(url,data)
	return createGroupdata['result']['groupids'][0]
#	if createGroupdata['error'][0]['message'] in "Invalid params.":
#		print "this group is exist"
#		return getGroupIP()
#	else:
#		return createGroupdata['result'][0]['groupids']

def getGroupID():
	data = json.dumps({
		"jsonrpc": "2.0",
    		"method": "hostgroup.get",
    		"params": {
        		"output": "extend",
        		"filter": {
        		    "name": ["{{ group_name }}"]
        		}
    		},
    		"auth": auth(),
    		"id": 103
	})
	groupidrespones = getdata(url,data)
	if len(groupidrespones['result']) == 0:
                return createGroup()
        else:
                return groupidrespones['result'][0]['groupid']

def getTemplateID():    
        data = json.dumps({
                "jsonrpc": "2.0",
                "method": "template.get",
                "params": {
                        "output": "extend",
                        "filter": {
                                "host": [
                                        "{{ template_name }}",
                                ]
                        }
                },
                "auth": auth(),
                "id": 106
        })
        templateresponse = getdata(url,data)
        if len(templateresponse['result']) == 0:
                return createTemplate()
        else:
                return templateresponse['result'][0]['templateid']	


if __name__ == '__main__':
	auth()
