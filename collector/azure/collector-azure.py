from subprocess import Popen, PIPE
import requests
import sys
import json
from pprint import pprint
import logging
import time

#logging.basicConfig(filename='./output.log', level=logging.DEBUG)
root = logging.getLogger()
root.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)

logging.debug("START Get access token")

with open('./auth.json', 'r') as myfile:
    data=myfile.read()
auth = json.loads(data)

url = 'https://login.microsoftonline.com/cef04b19-7776-4a94-b89b-375c77a8f936/oauth2/token'
response = requests.post(url, data = auth)
response = json.loads(response.text)
access_token = response["access_token"]

logging.debug("END Get access token")

subscription = auth["subscription"]

#command = 'curl -X GET -H "Authorization: Bearer '+access_token+'" https://management.azure.com/subscriptions/'+auth["subscription"]+'/providers/Microsoft.Web/sites?api-version=2016-08-01'
#print(command)

#p = Popen(command.split(" "), stdin=PIPE, stdout=PIPE, stderr=PIPE)
#output, err = p.communicate(b"input data that is passed to subprocess' stdin")
#rc = p.returncode
#print(output)
#sys.exit()

logging.debug("START Get providers")

url = 'https://management.azure.com/subscriptions/'+subscription+'/providers?api-version=2019-10-01'
headers = {"Authorization": "Bearer "+access_token}
response = requests.get(url, data={}, headers=headers)
response = json.loads(response.text)
providers = response

logging.debug("END Get providers")

logging.debug("START iterate providers")

logging.info("Found # of providers: "+str(len(providers["value"])))

for provider in providers["value"]:
    if "Microsoft.ContainerService" not in provider["id"]: continue

    logging.debug("START process provider "+provider["id"])

    logging.info("Found # of resources: "+str(len(provider["resourceTypes"])))

    resource_result = []
    resource_name = None
    for resource_type in provider["resourceTypes"]:
        name = resource_type['resourceType']
        api = resource_type['apiVersions'][0]
        #print(name+"\n")
        #print(api+"\n")
        #continue

        logging.debug("START process resource "+name)

        logging.debug("START request resource info "+name)

        resource_name = provider["id"]+'__'+name+'_'+api
        resource_name = resource_name.replace("/", "_")
        url = 'https://management.azure.com'+provider["id"]+'/'+name+'?api-version='+api
        #print(url)
        headers = {"Authorization": "Bearer "+access_token}
        response = requests.get(url, data={}, headers=headers)
        
        logging.debug("END request resource info "+name)

        logging.debug("Sleep for 1s")
        time.sleep(1)

        if response.status_code != 200:
            logging.error("Status code "+str(response.status_code)+" when requesting "+url)
            continue
        
        logging.debug("START get resource values")


        response_json = json.loads(response.text)
        logging.info("Found # of resource values: "+str(len(response_json["value"])))
        for value in response_json["value"]:
            resource_result.append(value)

        logging.debug("END get resource values")

        logging.debug("END process resource "+name)
    
    logging.debug("END process provider "+provider["id"])


    file_path= "../../data/"+resource_name+".json"
    
    logging.debug("START write file "+file_path)

    #pprint(resource_result)
    resource_result = json.dumps(resource_result)
    file = open("../../data/"+resource_name+".json","w")  
    file.write(resource_result)
    file.close()

    logging.debug("END write file "+file_path)

logging.debug("END iterate providers")