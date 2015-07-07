class Encoder():
    def encode(self, msg):
    	results = []
    	try:
    		for json_obj in json.loads(msg):
    			timestamp = int(json_obj['time'])
    			tags = {}
    			tags['host'] = json_obj['host']
    			if json_obj['plugin_instance'] != u'':
    				tags['plugin_instance'] = json_obj['plugin_instance']
    			if json_obj['type_instance'] != u'':
    				tags['type_instance'] = json_obj['type_instance']
    			if json_obj['type'] != u'':
    				tags['type'] = json_obj['type']
    			for i in range (0, len(json_obj['values'])):

    				if json_obj['dstypes'][i] != u'':
    					tags['ds_type'] = json_obj['dstypes'][i]
    				else:
    					del tags['ds_type'] #in case this has been set in a previous loop iteration
    				if json_obj['dsnames'][i] != u'':
    					tags['ds_name'] = json_obj['dsnames'][i]
    				else:
    					del tags['ds_name'] #in case this has been set in a previous loop iteration
    				new_point = {"precision":"s"}
    				new_point["name"] = json_obj['plugin']
    				new_point["timestamp"] = timestamp
    				new_point["tags"] = tags

    				new_point["fields"] = {"value" : json_obj['values'][i]}
    				results.append(new_point)
    	except Exception as inst:
    		error_log("Exception caught in json transformation: %s" % inst)
    	return results
