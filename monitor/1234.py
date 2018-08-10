	data = json.dumps({
	        "jsonrpc": "2.0",
	        "method": "action.create",
	        "params": {
                        "name": "vpn2",
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
						"value": "vpn2",
						"operator": 2,
					}
				],
			},
			"operations": [
				{
					"operationtype": 4,
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
