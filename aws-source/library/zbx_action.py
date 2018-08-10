#!/usr/bin/env python
'''
 Ansible module for zabbix actions
'''
import json
import requests
# import httplib

class ZabbixAPIError(Exception):
    '''
        ZabbixAPIError
        Exists to propagate errors up from the api
    '''
    pass

class ZabbixAPI(object):
    '''
        ZabbixAPI class
    '''

    def __init__(self, server, user, password, ssl_verify=False):
        if any([value == None for value in [server, user, password]]):
            raise ZabbixAPIError('Please specify zabbix server url, username, and password.')

        self.server = server+'/api_jsonrpc.php'
        self.ssl_verify = ssl_verify
        self.auth = None

        content = self.uri('user.login', user=user, password=password)

        if content.has_key('result'):
            self.auth = content['result']
	    print self.auth
        else:
            raise ZabbixAPIError("Unable to authenticate with zabbix server. {0} ".format(content['error']))

    def uri(self, method, params=None, **rpc_params):

        jsonrpc = "2.0"
        rid = 1

        headers = {}
        headers["Content-type"] = "application/json"

        if not params: params = rpc_params
        if not params: params = {}


        body = {
            "jsonrpc": jsonrpc,
            "method":  method,
            "params":  params,
            "id":      rid,
        }

        if method not in ['user.login', 'api.version']:
            body['auth'] = self.auth

        body = json.dumps(body)

        request = requests.Request("POST", self.server, data=body, headers=headers)
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

CUSTOM_SCRIPT_ACTION = '0'
IPMI_ACTION = '1'
SSH_ACTION = '2'
TELNET_ACTION = '3'
GLOBAL_SCRIPT_ACTION = '4'

EXECUTE_ON_ZABBIX_AGENT = '0'
EXECUTE_ON_ZABBIX_SERVER = '1'

OPERATION_REMOTE_COMMAND = '1'


def get_object_id_by_name(zapi, obj, name):
    _info = { 'host': {'f_key': 'name', 'id':'hostid'},
              'hostgroup': {'f_key':'name', 'id':'groupid'},
              'user': {'f_key':'alias', 'id':'userid'},
              'usergroup': {'f_key':'name', 'id':'usergrpid'},
              'mediatype': {'f_key':'description', 'id':'mediatypeid'},
              'template': {'f_key':'host', 'id':'templateid'},
              'script': {'f_key':'name', 'id':'scriptid'},
    }
    
 #   if obj == 'hostgroup':
 #       module = AnsibleModule(
 #           argument_spec=dict(
 #       	zbx_server=dict(required=True, type='str'),
 #       	zbx_user=dict(required=True, type='str'),
 #       	zbx_password=dict(required=True, type='str'),
 #               name=dict(required=True, type='str'),
 #               status=dict(default='enabled', type='str'),
 #               state=dict(default='present', type='str'),
 #       	),
 #       )
 #       content = zapi.uri(obj+'.get', {'filter': {_info[obj]['f_key']: name}})
 #       if len(content['result']) == 0:
 #           params = {'name': module.params['name'],}
 #           content = conn.uri('hostgroup.create', params)
 #           module.exit_json(changed=True, results=content, state='present')
 #           content = zapi.uri(obj+'.get', {'filter': {_info[obj]['f_key']: name}})
 #       else:	
 #           content = zapi.uri(obj+'.get', {'filter': {_info[obj]['f_key']: name}})
 #   else:
    content = zapi.uri(obj+'.get', {'filter': {_info[obj]['f_key']: name}})
    return _info[obj]['id'], content['result'][0][_info[obj]['id']]

def get_objects(zapi, obj, names):
    objs = []

    for name in names:
        key, oid = get_object_id_by_name(zapi, obj, name)
        objs.append({key: oid})

    return objs
    
def exists(content, key='result'):
    if not content.has_key(key):
        return False

    if not content[key]:
        return False

    return True

def conditions_equal(zab_conditions, user_conditions):
    c_type = 'conditiontype'
    _op = 'operator'
    val = 'value'
    if len(user_conditions) != len(zab_conditions):
        return False

    for zab_cond, user_cond in zip(zab_conditions, user_conditions):
        if zab_cond[c_type] != str(user_cond[c_type]) or zab_cond[_op] != str(user_cond[_op]) or \
           zab_cond[val] != str(user_cond[val]):
            return False

    return True

def filter_differences(zabbix_filters, user_filters):
    rval = {}
    for key, val in user_filters.items():

        if key == 'conditions':
            if not conditions_equal(zabbix_filters[key], val):
                rval[key] = val

        elif zabbix_filters[key] != str(val):
            rval[key] = val

    return rval

def opconditions_diff(zab_val, user_val):
    if len(zab_val) != len(user_val):
        return True

    for z_cond, u_cond in zip(zab_val, user_val):
        if not all([str(u_cond[op_key]) == z_cond[op_key] for op_key in \
                    ['conditiontype', 'operator', 'value']]):
            return True

    return False

def opmessage_diff(zab_val, user_val):
    for op_msg_key, op_msg_val in user_val.items():
        if zab_val[op_msg_key] != str(op_msg_val):
            return True

    return False

def opmessage_grp_diff(zab_val, user_val):
    zab_grp_ids = set([ugrp['usrgrpid'] for ugrp in zab_val])
    usr_grp_ids = set([ugrp['usrgrpid'] for ugrp in user_val])
    if usr_grp_ids != zab_grp_ids:
        return True

    return False

def opmessage_usr_diff(zab_val, user_val):
    zab_usr_ids = set([usr['userid'] for usr in zab_val])
    usr_ids = set([usr['userid'] for usr in user_val])
    if usr_ids != zab_usr_ids:
        return True

    return False

def opcommand_diff(zab_op_cmd, usr_op_cmd):
    for usr_op_cmd_key, usr_op_cmd_val in usr_op_cmd.items():
        if zab_op_cmd[usr_op_cmd_key] != str(usr_op_cmd_val):
            return True
    return False

def host_in_zabbix(zab_hosts, usr_host):

    for usr_hst_key, usr_hst_val in usr_host.items():
        for zab_host in zab_hosts:
            if usr_hst_key in zab_host and \
               zab_host[usr_hst_key] == str(usr_hst_val):
                return True

    return False

def hostlist_in_zabbix(zab_hosts, usr_hosts):

    if len(zab_hosts) != len(usr_hosts):
        return False

    for usr_host in usr_hosts:
        if not host_in_zabbix(zab_hosts, usr_host):
            return False

    return True

def operation_differences(zabbix_ops, user_ops):
    if len(zabbix_ops) != len(user_ops):
        return user_ops

    rval = {}
    for zab, user in zip(zabbix_ops, user_ops):
        for oper in user.keys():
            if oper == 'opconditions' and opconditions_diff(zab[oper], user[oper]):
                rval[oper] = user[oper]

            elif oper == 'opmessage' and opmessage_diff(zab[oper], user[oper]):
                rval[oper] = user[oper]

            elif oper == 'opmessage_grp' and opmessage_grp_diff(zab[oper], user[oper]):
                rval[oper] = user[oper]

            elif oper == 'opmessage_usr' and opmessage_usr_diff(zab[oper], user[oper]):
                rval[oper] = user[oper]

            elif oper == 'opcommand' and opcommand_diff(zab[oper], user[oper]):
                rval[oper] = user[oper]

            elif oper == 'opcommand_hst' or oper == 'opcommand_grp':
                if not hostlist_in_zabbix(zab[oper], user[oper]):
                    rval[oper] = user[oper]

            elif oper not in ['opconditions', 'opmessage', 'opmessage_grp',
                              'opmessage_usr', 'opcommand', 'opcommand_hst',
                              'opcommand_grp'] and str(zab[oper]) != str(user[oper]):
                rval[oper] = user[oper]

    return rval

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

def get_event_source(from_src):
    choices = ['trigger', 'discovery', 'auto', 'internal']
    rval = 0
    try:
        rval = choices.index(from_src)
    except ValueError as _:
        ZabbixAPIError('Value not found for event source [%s]' % from_src)

    return rval

def get_condition_operator(inc_operator):
    vals = {'=': 0,
            '<>': 1,
            'like': 2,
            'not like': 3,
            'in': 4,
            '>=': 5,
            '<=': 6,
            'not in': 7,
           }

    return vals[inc_operator]

def get_trigger_value(inc_trigger):
    rval = 1
    if inc_trigger == 'PROBLEM':
        rval = 1
    else:
        rval = 0

    return rval

def get_condition_type(event_source, inc_condition):
    c_types = {}
    if event_source == 'trigger':
        c_types = {'host group': 0,
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
        c_types = {'host IP': 7,
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
        c_types = {'proxy': 20,
                   'host name': 22,
                   'host metadata': 24,
                  }

    elif event_source == 'internal':
        c_types = {'host group': 0,
                   'host': 1,
                   'host template': 13,
                   'application': 15,
                   'event type': 23,
                  }
    else:
        raise ZabbixAPIError('Unkown event source %s' % event_source)

    return c_types[inc_condition]

def get_operation_type(inc_operation):
    o_types = {'send message': 0,
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

    return o_types[inc_operation]

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

        if operation['operationtype'] == 0: # send message.  Need to fix the
            operation['opmessage']['mediatypeid'] = \
             get_object_id_by_name(zapi, 'mediatypeid', operation['opmessage']['mediatypeid'])[1]
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

def get_operation_evaltype(inc_type):
    rval = 0
    if inc_type == 'and/or':
        rval = 0
    elif inc_type == 'and':
        rval = 1
    elif inc_type == 'or':
        rval = 2
    elif inc_type == 'custom':
        rval = 3

    return rval

def get_action_conditions(zapi, event_source, inc_conditions):
    inc_conditions['evaltype'] = get_operation_evaltype(inc_conditions['evaltype'])

    for cond in inc_conditions['conditions']:

        cond['operator'] = get_condition_operator(cond['operator'])
        cond['conditiontype'] = get_condition_type(event_source, cond['conditiontype'])
        if cond['conditiontype'] == 0:
            cond['value'] = get_object_id_by_name(zapi, 'hostgroup', cond['value'])
        elif cond['conditiontype'] == 1:
            cond['value'] = get_object_id_by_name(zapi, 'host', cond['value'])
        elif cond['conditiontype'] == 4:
            cond['value'] = get_priority(cond['value'])
        elif cond['conditiontype'] == 5:
            cond['value'] = get_trigger_value(cond['value'])
        elif cond['conditiontype'] == 13:
            cond['value'] = get_object_id_by_name(zapi, 'template', cond['value'])
        elif cond['conditiontype'] == 16:
            cond['value'] = ''

    return inc_conditions

def main():
    '''
    ansible zabbix module for zbx_action
    '''

    module = AnsibleModule(
        argument_spec=dict(
            zbx_server=dict(required=True, type='str'),
            zbx_user=dict(required=True, type='str'),
            zbx_password=dict(required=True, type='str'),
            name=dict(required=True, type='str'),
            event_source=dict(default='auto', choices=['trigger', 'discovery', 'auto', 'internal'], type='str'),
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

    conn = ZabbixAPI(module.params['zbx_server'], module.params['zbx_user'], module.params['zbx_password'])

    state = module.params['state']

    content = conn.uri('action.get',
                               {'filter': {'name': module.params['name']},
                                'selectFilter': 'extend',
                                'selectOperations': 'extend',
                               })

    if state == 'list':
        module.exit_json(changed=False, results=content['result'], state="list")

    if state == 'absent':
        if not exists(content):
            module.exit_json(changed=False, state="absent")

        content = conn.uri('action.delete', [content['result'][0]['actionid']])
        module.exit_json(changed=True, results=content['result'], state="absent")

    # Create and Update
    if state == 'present':

        conditions = get_action_conditions(conn, module.params['event_source'], module.params['conditions_filter'])
        operations = get_action_operations(module, conn, module.params['operations'])

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
                  'eventsource': get_event_source(module.params['event_source']),
                  'status': int(module.params['status']!='enabled'),
                  'def_shortdata': def_shortdata,
                  'def_longdata': def_longdata,
                  'r_shortdata': r_shortdata,
                  'r_longdata': r_longdata,
#                  'recovery_msg': int(module.params['send_recovery']),
                  'filter': conditions,
                  'operations': operations,
                 }

        _ = [params.pop(key, None) for key in params.keys() if params[key] is None]

        # CREATE
        if not exists(content):
            content = conn.uri('action.create', params)

            if content.has_key('error'):
                module.exit_json(failed=True, changed=True, results=content['error'], state="present")

            module.exit_json(changed=True, results=content['result'], state='present')


        # UPDATE
#        _ = params.pop('hostid', None)
        differences = {}
        zab_results = content['result'][0]
        for key, value in params.items():

            if key == 'operations':
                ops = operation_differences(zab_results[key], value)
                if ops:
                    differences[key] = ops

            elif key == 'filter':
                filters = filter_differences(zab_results[key], value)
                if filters:
                    differences[key] = filters

            elif zab_results[key] != value and zab_results[key] != str(value):
                differences[key] = value

        if not differences:
            module.exit_json(changed=False, results=zab_results, state="present")

        differences['actionid'] = zab_results['actionid']
        differences['operations'] = params['operations']
        differences['filter'] = params['filter']
        content = conn.uri('action.update', differences)

        if content.has_key('error'):
            module.exit_json(failed=True, changed=False, results=content['error'], state="present")

        module.exit_json(changed=True, results=content['result'], state="present")

    module.exit_json(failed=True,
                     changed=False,
                     results='Unknown state passed. %s' % state,
                     state="unknown")









from ansible.module_utils.basic import *

main()
#hostgroup(None)
