#!/usr/bin/python3
import json
import yaml

from ansible.module_utils.basic import AnsibleModule

#VIOL_URL_LENGTH
def url_length(policy_json, name, length):
	if "filetypes" in policy_json["policy"] :
		filetype_exists, x = key_exists(policy_json["policy"]["filetypes"], "name", name)
		if filetype_exists:
			if check_value(policy_json["policy"]["filetypes"][x], "urlLength", length):
				return policy_json, False, "<b>Error!</b> Same URL Length already configured"
			else:
				policy_json["policy"]["filetypes"][x]["urlLength"] = length
				if not "checkUrlLength" in policy_json["policy"]["filetypes"][x]:
					policy_json["policy"]["filetypes"][x]["checkUrlLength"] = True					
		else:
			policy_json["policy"]["filetypes"].append(json.loads('{"name":"'+name+'","urlLength":'+str(length)+', "checkUrlLength":true}'))
	else:
		policy_json["policy"]["filetypes"] = json.loads('[{"name":"'+name+'","urlLength":'+str(length)+', "checkUrlLength":true}]')
	
	return policy_json, True, "Success! URL Length adjusted to " + str(length)
#VIOL_POST_DATA_LENGTH
def postdata_length(policy_json, name, length):
	if "filetypes" in policy_json["policy"] :
		filetype_exists, x = key_exists(policy_json["policy"]["filetypes"], "name", name)
		if filetype_exists:
			if check_value(policy_json["policy"]["filetypes"][x], "postDataLength", length):
				return policy_json, False, "<b>Error!</b> Same PostData Length already configured"
			else:
				policy_json["policy"]["filetypes"][x]["postDataLength"] = length
				if not "checkPostDataLength" in policy_json["policy"]["filetypes"][x]:
					policy_json["policy"]["filetypes"][x]["checkPostDataLength"] = True				
		else:
			policy_json["policy"]["filetypes"].append(json.loads('{"name":"'+name+'","postDataLength":'+str(length)+', "checkPostDataLength":true}'))
	else:
		policy_json["policy"]["filetypes"] = json.loads('[{"name":"'+name+'","postDataLength":'+str(length)+', "checkPostDataLength":true}]')
	
	return policy_json, True, "Success! PostData Length adjusted to " + str(length)
#VIOL_QUERY_STRING_LENGTH
def querystring_length(policy_json, name, length):
	if "filetypes" in policy_json["policy"] :
		filetype_exists, x = key_exists(policy_json["policy"]["filetypes"], "name", name)
		if filetype_exists:
			if check_value(policy_json["policy"]["filetypes"][x], "queryStringLength", length):
				return policy_json, False, "<b>Error!</b> Same QueryString Length already configured"
			else:
				policy_json["policy"]["filetypes"][x]["queryStringLength"] = length
				if not "checkQueryStringLength" in policy_json["policy"]["filetypes"][x]:
					policy_json["policy"]["filetypes"][x]["checkQueryStringLength"] = True
		else:
			policy_json["policy"]["filetypes"].append(json.loads('{"name":"'+name+'","queryStringLength":'+str(length)+', "checkQueryStringLength":true}'))
	else:
		policy_json["policy"]["filetypes"] = json.loads('[{"name":"'+name+'","queryStringLength":'+str(length)+', "checkQueryStringLength":true}]')
	
	return policy_json, True, "Success! QueryString Length adjusted to " + str(length)
#VIOL_REQUEST_LENGTH
def request_length(policy_json, name, length):
	if "filetypes" in policy_json["policy"] :
		filetype_exists, x = key_exists(policy_json["policy"]["filetypes"], "name", name)
		if filetype_exists:
			if check_value(policy_json["policy"]["filetypes"][x], "requestLength", length):
				return policy_json, False, "<b>Error!</b> Same RequestLength Length already configured"
			else:
				policy_json["policy"]["filetypes"][x]["requestLength"] = length
				if not "checkRequestLength" in policy_json["policy"]["filetypes"][x]:
					policy_json["policy"]["filetypes"][x]["checkRequestLength"] = True									
		else:
			policy_json["policy"]["filetypes"].append(json.loads('{"name":"'+name+'","requestLength":'+str(length)+', "checkRequestLength":true}'))
	else:
		policy_json["policy"]["filetypes"] = json.loads('[{"name":"'+name+'","requestLength":'+str(length)+', "checkRequestLength":true}]')
	
	return policy_json, True, "Success! RequestLength Length adjusted to " + str(length)

def key_exists(mod_json, key, value):
  x = 0
  exists = False
  for i in mod_json:
    if key in i:
      if i[key] == value:
        exists = True
        break;
    x = x + 1
  return (exists, x)

def check_value(mod_json, key, value):
  try:
    if mod_json[key] == value:
      return True
    else: 
      return False
  except (KeyError , TypeError):
    return False

def main():
    module = AnsibleModule(
        argument_spec=dict(
            policy_path=dict(type='str', required=True),
            filetype=dict(type='str', required=True),
            format=dict(type='str', required=True),
            type=dict(type='str', required=True),
            length=dict(type='int', required=True)
        )
    )

    policy_path = module.params['policy_path']
    filetype = module.params['filetype']
    format = module.params['format'].lower()
    length = module.params['length']
    if module.params['type'] is not None:
      type = module.params['type'].lower()
    else:
      type = module.params['type']

      
    allowed_values = ["url", "request", "post_data", "qs_data"]
    if type != None and type not in allowed_values :
      module.fail_json(msg=f"'{type}' is  not a valid value for the 'type' variable. It can be any of the following: {list(allowed_values)}.")
    
    try:
        with open(policy_path, 'r') as file:
          policy = file.read()
    except Exception as e:
        module.fail_json(msg=f"Failed to read file: {str(e)}")


    if (format == "yaml"):
      try:
        yData = yaml.safe_load(policy)
        jData = yData["spec"]
      except:
        module.fail_json(msg=f"Input file not YAML")
    else:
      try:
        jData = json.loads(policy)
      except:
        module.fail_json(msg=f"Input file not JSON")


   
    if type=="url":
      jData, result, msg = url_length(jData,filetype,length)
    if type=="request":
      jData, result, msg = request_length(jData,filetype,length)
    if type=="post_data":
      jData, result, msg = postdata_length(jData,filetype,length)
    if type=="qs_data":
      jData, result, msg = querystring_length(jData,sig_id,length)

    if result :   
      # if there is a change in the policy, update the file with the new policy and exit the module with a "changed" option
      if (format == "yaml"):
        yData["spec"] = jData
        with open('policy_mod', 'w', encoding='utf-8') as f: 
          yaml.dump(yData, f, indent=2) #Save the json format of the policy
        module.exit_json(changed=True, msg=msg, policy=yData) #Exit and provide the yaml format of the policy
      else:
        with open('policy_mod', 'w', encoding='utf-8') as f:
          json.dump(jData, f, ensure_ascii=False, indent=2) #Save the json format of the policy
        module.exit_json(changed=True, msg=msg, policy=jData)  #Exit and provide the json format of the policy
    else :
      if (format == "yaml"):  # if no change exit the module with a "No change" option
        module.exit_json(changed=False, msg=msg, policy=yData)  #Exit and provide the yaml format of the policy
      else:
        module.exit_json(changed=False, msg=msg, policy=jData)  #Exit and provide the json format of the policy

    

if __name__ == '__main__':
    main()