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

#		if response.status_code not in [200, 201]:
#			raise ZabbixAPIError('Error calling zabbix.  Zabbix returned %s' % response.status_code)

#        	try:
#        		content = response.json()
#                except ValueError as err:
#	                content = {"error": err.message}
		content = response.json()
        
#		print content
                return content

CUSTOM_SCRIPT_ACTION = '0'
IPMI_ACTION = '1'
SSH_ACTION = '2'
TELNET_ACTION = '3'
GLOBAL_SCRIPT_ACTION = '4'

EXECUTE_ON_ZABBIX_AGENT = '0'
EXECUTE_ON_ZABBIX_SERVER = '1'

OPERATION_REMOTE_COMMAND = '1'





def exists(content, key='result'):
	print content.has_key
	if not content.has_key(key):
		return False
	
	if not content[key]:
		return False
	return True

def get_objects(zapi, obj, names):
    	objs = []

    	for name in names:
        	key, oid = get_object_id_by_name(zapi, obj, name)
        	objs.append({key: oid})

   	return objs

def get_opcommand_type(opcommand_type):
    	oc_types = {'custom script': CUSTOM_SCRIPT_ACTION,
                    'IPMI': IPMI_ACTION,
                    'SSH': SSH_ACTION,
                    'Telnet': TELNET_ACTION,
                    'global script': GLOBAL_SCRIPT_ACTION,
                   }

    	return oc_types[opcommand_type]


def get_execute_on(execute_on):
    	e_types = {'zabbix agent': EXECUTE_ON_ZABBIX_AGENT,
                   'zabbix server': EXECUTE_ON_ZABBIX_SERVER,
               	  }

    	return e_types[execute_on]



def action_remote_command(ansible_module, zapi, operation):
    	if 'type' not in operation['opcommand']:
        	ansible_module.exit_json(failed=True, changed=False, state='unknown',
                                 results="No Operation Type provided")

    	operation['opcommand']['type'] = get_opcommand_type(operation['opcommand']['type'])

    	if operation['opcommand']['type'] == CUSTOM_SCRIPT_ACTION:

        	if 'execute_on' in operation['opcommand']:
            		operation['opcommand']['execute_on'] = get_execute_on(operation['opcommand']['execute_on'])
		operation['opcommand_hst'] = []
        	operation['opcommand_grp'] = []
        	for usr_host in operation['target_hosts']:
            		if usr_host['type'] == 'zabbix server':
                		operation['opcommand_hst'].append({'hostid': 0})
            		elif usr_host['type'] == 'group':
                		group_name = usr_host['target']
                		_, gid = get_object_id_by_name(zapi, 'hostgroup',group_name)
				operation['opcommand_grp'].append({'groupid': gid})
            		elif usr_host['type'] == 'host':
                		host_name = usr_host['target']
                		_, hid = get_object_id_by_name(zapi, 'host', host_name)
                		operation['opcommand_hst'].append({'hostid': hid})
            		elif user_host['type'] == 'hosts':
                		operation['opcommand_hst'].extend(get_objects(zapi, 'host',usr_host['target']))
            		elif user_host['type'] == 'groups':
                		operation['opcommand_grp'].extend(get_objects(zapi, 'group',usr_host['target']))
        	del operation['target_hosts']
    	else:
        	ansible_module.exit_json(failed=True, changed=False, state='unknown',
                                 results="Unsupported remote command type")


def get_action_operations(ansible_module, zapi, inc_operations):
	for operation in inc_operations:
		operation['operationtype'] = get_operation_type(operation['operationtype'])
		if operation['operationtype'] == 0:
			operation['opmessage']['mediatypeid'] = get_object_id_by_name(zapi, 'mediatypeid', operation['opmessage']['mediatypeid'])[1]
			operation['opmessage_grp'] = get_objects(zapi, 'usergroup',operation.get('opmessage_grp', []))
			operation['opmessage_usr'] = get_objects(zapi, 'user',operation.get('opmessage_usr', []))
			if operation['opmessage']['default_msg']:
				operation['opmessage']['default_msg'] = 1
			else:
				operation['opmessage']['default_msg'] = 0
		if operation['operationtype'] == OPERATION_REMOTE_COMMAND:
			action_remote_command(ansible_module, zapi, operation)
		if operation['operationtype'] == 4:
			operation['opgroup'] = get_objects(zapi, 'hostgroup', operation['opgroup'])
		if operation['operationtype'] == 6:
			operation['optemplate'] = get_objects(zapi, 'template', operation['optemplate'])
		if operation.has_key('opconditions'):
			operation['optemplate'] = get_objects(zapi, 'template', operation['optemplate'])
		if operation.has_key('opconditions'):
			for condition in operation['opconditions']:
				if condition['conditiontype'] == 'event acknowledged':
					condition['conditiontype'] = 14
				if condition['operator'] == '=':
					condition['operator'] = 0
				if condition['value'] == 'acknowledged':
					condition['value'] = 1
				else:
					condition['value'] = 0
	return inc_operations	


def get_operation_type(operation):
	operation_type = {'send message': 0,
           		  'remote command': OPERATION_REMOTE_COMMAND,
                          'add host': 2,
                          'remove host': 3,
                          'add to host group': 4,
                          'remove from host group': 5,
                          'link to template': 6,
                          'unlink from template': 7,
                          'enable host': 8,
                          'disable host': 9,	
			}
	return operation_type[operation]





def get_operation_evaltype(evaltype):
	way_to_value = 0
	if evaltype == 'and/or':
		way_to_value = 0
	elif evaltype == 'and':
		way_to_value = 1
	elif evaltype == 'or':
		way_to_value = 2
	elif evaltype == 'custom':
		way_to_value = 3
	
	return way_to_value

def get_condition_operator(operator):
	value = {'=': 0,
                 '<>': 1,
                 'like': 2,
                 'not like': 3,
                 'in': 4,
                 '>=': 5,
                 '<=': 6,
                 'not in': 7,
           }
	return value[operator]

def get_condition_type(event_source, condition):
	condition_type = {}
	if event_source == 'trigger':
		condition_type = {'host group': 0,
                                  'host': 1,
                                  'trigger': 2,
                                  'trigger name': 3,
                                  'trigger severity': 4,
                                  'trigger value': 5,
                                  'time period': 6,
                                  'host template': 13,
                                  'application': 15,
                                  'maintenance status': 16,
                  	         }
	
	elif event_source == 'discovery':
		condition_type = {'host IP': 7,
                                  'discovered service type': 8,
                                  'discovered service port': 9,
                                  'discovery status': 10,
                                  'uptime or downtime duration': 11,
                                  'received value': 12,
                                  'discovery rule': 18,
                                  'discovery check': 19,
                                  'proxy': 20,
                                  'discovery object': 21,
                                 }

	elif event_source == 'auto':
		condition_type = {'proxy': 20,
                                  'host name': 22,
                                  'host metadata': 24,
                                 }

	elif event_source == 'internal':
		condition_type = {'host group': 0,
                                  'host': 1,
                                  'host template': 13,
                                  'application': 15,
                                  'event type': 23,
                                 }
	
	else:
		print "Unkown event source %s" % event_source
	
	return condition_type[condition]


def get_action_conditions(zapi, event_source, inc_conditions):
	inc_conditions['evaltype'] = get_operation_evaltype(inc_conditions['evaltype'])
	for condition in inc_conditions['conditions']:
		condition['operator'] = get_condition_operator(condition['operator'])
		condition['conditiontype'] = get_condition_type(event_source, condition['conditiontype'])
		
		if condition['conditiontype'] == 0:
			condition['value'] = get_object_id_by_name(zapi, 'hostgroup', condition['value'])
        	elif condition['conditiontype'] == 1:
        		condition['value'] = get_object_id_by_name(zapi, 'host', condition['value'])
        	elif condition['conditiontype'] == 4:
        		condition['value'] = get_priority(condition['value'])
        	elif condition['conditiontype'] == 5:
        	    	condition['value'] = get_trigger_value(condition['value'])
        	elif condition['conditiontype'] == 13:
        	    	condition['value'] = get_object_id_by_name(zapi, 'template', condition['value'])
        	elif condition['conditiontype'] == 16:
        	    	condition['value'] = ''	

	return inc_conditions

def get_object_id_by_name(zapi, obj, name):
	_info = { 'host': {'f_key': 'name', 'id':'hostid'},
                  'hostgroup': {'f_key':'name', 'id':'groupid'},
                  'user': {'f_key':'alias', 'id':'userid'},
                  'usergroup': {'f_key':'name', 'id':'usergrpid'},
                  'mediatype': {'f_key':'description', 'id':'mediatypeid'},
                  'template': {'f_key':'host', 'id':'templateid'},
                  'script': {'f_key':'name', 'id':'scriptid'},
	}
	content = zapi.uri(obj+'.get', {'filter': {_info[obj]['f_key']: name}})

	return _info[obj]['id'], content['result'][0][_info[obj]['id']]


def get_priority(priority):
    	prior = 0
    	if 'info' in priority:
        	prior = 1
    	elif 'warn' in priority:
        	prior = 2
    	elif 'avg' == priority or 'ave' in priority:
        	prior = 3
    	elif 'high' in priority:
        	prior = 4
    	elif 'dis' in priority:
        	prior = 5

    	return prior

def get_trigger_value(trigger):
	rval = 1
    	if trigger == 'PROBLEM':
        	rval = 1
    	else:
        	rval = 0

    	return rval



def get_eventsource(from_src):
    	choices = ['trigger', 'discovery', 'auto', 'internal']
    	rval = 0
    	try:
    	    rval = choices.index(from_src)
    	except ValueError as _:
    	    ZabbixAPIError('Value not found for event source [%s]' % from_src)

    	return rval



def main():
	'''
	ansible zabbix module for zabbix_action
	'''

	module = AnsibleModule(
		argument_spec=dict(
			zabbix_server=dict(required=True, type='str'),
			zabbix_user=dict(required=True, type='str'),
			zabbix_password=dict(required=True, type='str'),
	                event_source=dict(default='auto', choices=['trigger', 'discovery', 'auto', 'internal'], type='str'),
			name=dict(required=True, type='str'),
	#		method=dict(required=True, type='str'),
	                action_subject=dict(default=None, type='str'),
	                action_message=dict(default=None, type='str'),
	                reply_subject=dict(default=None, type='str'),
	                reply_message=dict(default=None, type='str'),
	    #            send_recovery=dict(default=False, type='bool'),
	                status=dict(default='enabled', type='str'),
	                escalation_time=dict(default=60, type='int'),
	                conditions_filter=dict(default=None, type='dict'),
	                operations=dict(default=None, type='list'),
	                state=dict(default='present', type='str'),
		),
	            #supports_check_mode=True
	)


	conn = ZabbixAPI(module.params['zabbix_server'], module.params['zabbix_user'], module.params['zabbix_password'])

	state = module.params['state']
	content = conn.uri('action.get',
                          	{'output': 'extend',
                                 'selectFilter': 'extend',
                                 'selectOperations': 'extend',
				 'filter': {'name': [module.params['name']]}
				})
		

	if state == 'absent':
		if not exists(content):
			print content
			module.exit_json(changed=False, result=content, state="absent")
		else:
			print content
			content = conn.uri('action.delete', [content['result'][0]['actionid']])
			module.exit_json(changed=True, result=content, state='absent')




	if state == 'present':
		conditions = get_action_conditions(conn, module.params['event_source'], module.params['conditions_filter'])
		operations = get_action_operations(module, conn, module.params['operations'])
		#def_short

		def_shortdata = module.params['action_subject']
		def_longdata = module.params['action_message']
		if def_shortdata == None:
			if module.params['event_source'] == 'auto':
				def_shortdata = "Auto registration: {HOST.HOST}"
			if module.params['event_source'] == 'trigger':
				def_shortdata = "{TRIGGER.STATUS}: {TRIGGER.NAME}"
			if module.params['event_source'] == 'discovery':
				def_shortdata = "Discovery: {DISCOVERY.DEVICE.STATUS} {DISCOVERY.DEVICE.IPADDRESS}"
	
		if def_longdata == None:
			if module.params['event_source'] == 'auto':
		                def_longdata = "Host name: {HOST.HOST}\r\nHost IP: {HOST.IP}\r\nAgent port: {HOST.PORT}"
		        if module.params['event_source'] == 'trigger':
        		        def_longdata = "{TRIGGER.NAME}: {TRIGGER.STATUS}\r\nLast value: {ITEM.LASTVALUE}\r\n\r\n{TRIGGER.URL}"
        	        if module.params['event_source'] == 'discovery':
        		        def_longdata = "Discovery rule: {DISCOVERY.RULE.NAME}\r\nDevice IP:{DISCOVERY.DEVICE.IPADDRESS}\r\nDevice DNS: {DISCOVERY.DEVICE.DNS}\r\nDevice status: {DISCOVERY.DEVICE.STATUS}\r\nDevice uptime: {DISCOVERY.DEVICE.UPTIME}\r\n\r\nDevice service name: {DISCOVERY.SERVICE.NAME}\r\nDevice service port: {DISCOVERY.SERVICE.PORT}\r\nDevice service status: {DISCOVERY.SERVICE.STATUS}\r\nDevice service uptime: {DISCOVERY.SERVICE.UPTIME}"

		
		r_shortdata = module.params['reply_subject']
        	r_longdata = module.params['reply_message']
       		if r_shortdata == None:
            		if module.params['event_source'] == 'trigger':
       	        		r_shortdata = "{TRIGGER.NAME}: {TRIGGER.STATUS}"
        	if r_longdata == None:
            		if module.params['event_source'] == 'trigger':
                		r_longdata = "Trigger: {TRIGGER.NAME}\r\nTrigger status: {TRIGGER.STATUS}\r\n" + \
                               "Trigger severity: {TRIGGER.SEVERITY}\r\nTrigger URL: {TRIGGER.URL}\r\n\r\n" +  \
                               "Item values:\r\n\r\n1. {ITEM.NAME1} ({HOST.NAME1}:{ITEM.KEY1}): " +  \
                               "{ITEM.VALUE1}\r\n2. {ITEM.NAME2} ({HOST.NAME2}:{ITEM.KEY2}): " +  \
                               "{ITEM.VALUE2}\r\n3. {ITEM.NAME3} ({HOST.NAME3}:{ITEM.KEY3}): " +  \
                               "{ITEM.VALUE3}"



		params = {'name': module.params['name'],
			  'esc_period': module.params['escalation_time'],
			  'eventsource': get_eventsource(module.params['event_source']),
			  'status': int(module.params['status']!='enabled'),
			  'def_shortdata': def_shortdata,
                  	  'def_longdata': def_longdata,
                  	  'r_shortdata': r_shortdata,
                  	  'r_longdata': r_longdata,
			  'filter': conditions,
                  	  'operations': operations,
			}
#		_ = [params.pop(key, None) for key in params.keys() if params[key] is None
	
		if not exists(content):
			content = conn.uri('action.create', params)
		
			if content.has_key('error'):
				module.exit_json(failed=True, changed=True, results=content['error'], state='present')
			else:
				module.exit_json(changed=True, results=content, state='present')
		else:
			module.exit_json(changed=False, result=content, state="present")


        	differences = {}
        	zabbix_results = content['result'][0]
        	for key, value in params.items():
        		if key == 'operations':
        			ops = operation_differences(zabbix_results[key], value)
        			if ops:
					differences[key] = ops
			elif key == 'filter':
				filters = filter_differences(zabbix_results[key], value)
				if filters:
					differences[key] = filters
			elif zabbix_results[key] != value and zabbix_results[key] != str(value):
				differences[key] = value


		if not differences:
			module.exit_json(changed=False, results=zabbix_results, state="present")
		differences['actionid'] = zabbix_results['actionid']
		differences['operations'] = params['operations']
		differences['filter'] = params['filter']
        	content = conn.uri('action.update', differences)

		if content.has_key('error'):
			module.exit_json(failed=True, changed=False, resutls=content['error'], state="present")
		module.exit_json(changed=True, results=content['result'], state="present")
	

	




def operation_differences(zabbix_ops, user_ops):
	if len(zabbix_ops) != len(user_ops):
		return user_ops


#	rval = {}
#	for zabbix, user in zip(zabbix_ops, user_ops):
#		for oper in user.keys():
#			if 





	




from ansible.module_utils.basic import *

main()

