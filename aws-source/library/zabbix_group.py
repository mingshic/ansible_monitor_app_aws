#!/usr/bin/env python
import json
import requests

class ZabbixAPI(object):
	def __init__(self, server, user, password, ssl_verify=False):
	#	if any([value == None for value in [server, user, password]]):
	#		raise ZabbixAPIError('please user so on')
		self.server = server+'/api_jsonrpc.php'
		self.ssl_verify = ssl_verify
		self.auth = None
		content = self.uri('user.login', user=user, password=password)

		if content.has_key('result'):
			self.auth = content['result']
			print self.auth
	
#		else:
#			raise ZabbixAPIError("unable to auth")

	def uri(self, method, params=None, **rpc_params):
		headers = {}
		headers["Content-type"] = "application/json"

		if not params: 
			params = rpc_params
 	        if not params: 
			params = {}

		data = {
			"jsonrpc": 2.0,
			"method": method,
			"params": params,
			"id": 1,
		}
		if method not in ['user.login', 'api.version']:
			data['auth'] = self.auth
		data = json.dumps(data)

		request = requests.Request("POST", self.server, data=data, headers=headers)
		session = requests.Session()
		req_prep = session.prepare_request(request)
		response = session.send(req_prep, verify=self.ssl_verify)

		if response.status_code not in [200, 201]:
			raise ZabbixAPIError('Error calling zabbix.  Zabbix returned %s' % response.status_code)

        	try:
        		content = response.json()
                except ValueError as err:
	                content = {"error": err.message}
        
                return content

#CUSTOM_SCRIPT_ACTION = '0'
#IPMI_ACTION = '1'
#SSH_ACTION = '2'
#TELNET_ACTION = '3'
#GLOBAL_SCRIPT_ACTION = '4'
#
#EXECUTE_ON_ZABBIX_AGENT = '0'
#EXECUTE_ON_ZABBIX_SERVER = '1'
#
#OPERATION_REMOTE_COMMAND = '1'

def exists(content, key='result'):
	print content.has_key
	if not content.has_key(key):
		return False
	
	if not content[key]:
		return False
	return True


def main():
	'''
	ansible zabbix module for zabbix_action
	'''

	module = AnsibleModule(
		argument_spec=dict(
			zabbix_server=dict(required=True, type='str'),
			zabbix_user=dict(required=True, type='str'),
			zabbix_password=dict(required=True, type='str'),
	                group=dict(required=True, type='str'),
	                status=dict(default='enabled', type='str'),
	                state=dict(default='present', type='str'),
		),
	)


	conn = ZabbixAPI(module.params['zabbix_server'], module.params['zabbix_user'], module.params['zabbix_password'])

	state = module.params['state']
	content = conn.uri('hostgroup.get',
                          	{"output": "extend",
				 "filter": {'name': [module.params['group']]},
				})

	if state == 'absent':
		if not exists(content):
			module.exit_json(changed=False, result=content, state="absent")
		else:
			content = conn.uri('hostgroup.delete', [content['result'][0]['groupid']])
			module.exit_json(changed=True, result=content, state='absent')

	if state == 'present':
		params = {'name': module.params['group'],}
		if not exists(content):
			content = conn.uri('hostgroup.create', params)
		
			if content.has_key('error'):
				module.exit_json(failed=True, changed=True, results=content['error'], state='present')
			else:
				module.exit_json(changed=True, results=content, state='present')
		else:
			module.exit_json(changed=False, result=content, state="present")
from ansible.module_utils.basic import *

main()

