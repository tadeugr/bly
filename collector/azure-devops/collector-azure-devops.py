from subprocess import Popen, PIPE
import requests
import sys
import json
from pprint import pprint
import logging
import time
import urllib.parse
import uuid
import os.path

with open('./auth.json', 'r') as myfile:
    data=myfile.read()
_AUTH = json.loads(data)

_ORGANIZATION = _AUTH["organization"]
_WRITE_TO_FILE = []

def makeFileName(filename):
    keepcharacters = ('.','_', '-')
    result =  "".join(c for c in filename if c.isalnum() or c in keepcharacters).rstrip()
    return result

class Wiki:
    def __init__(self, attrs):
        self.pages = []
        for key, value in attrs.items():
            setattr(self, key, value)

    def setPages(self, value):
        self.pages = value

    def setPagesContent(self, pages):

        if "subPages" in pages and len(pages["subPages"]) > 0:
            for subpage in pages["subPages"]:
                self.setPagesContent(subpage)
        else:
            content = self.getPageContent(pages)
            pages["_bly_collector_content"] = content
            _WRITE_TO_FILE.append(pages)

    def getPageContent(self, page):

        if "path" not in page or page["path"] == "":
            logging.error("Page has no path: "+json.dumps(page))
            return ""

        url = 'https://dev.azure.com/'
        url += self.organization+'/'
        url += self.project_id+'/'
        url += '_apis/wiki/wikis/'
        url += self.wiki_id+'/'
        url += 'pages?api-version=5.1&path='
        url += urllib.parse.quote(page["path"])
        url += '&includeContent=True'

        response = requests.get(url, data={}, auth=(_AUTH["user"], _AUTH["token"]))
        response_obj = json.loads(response.text)

        if "innerException" in response_obj:
            logging.error("Error requesting "+url)
            if "message" in response_obj:
                logging.error(response_obj["message"])
            return ""

        return response_obj["content"]

    def getPages(self):
        return self.pages



#logging.basicConfig(filename='./output.log', level=logging.DEBUG)
root = logging.getLogger()
root.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)

with open('./auth.json', 'r') as myfile:
    data=myfile.read()
auth = json.loads(data)

logging.debug("START Get projects")

url = 'https://dev.azure.com/'+_ORGANIZATION+'/_apis/projects?api-version=2.0'
response = requests.get(url, data={}, auth=(_AUTH["user"], _AUTH["token"]))
response = json.loads(response.text)
projects = response

logging.debug("END Get projects")

logging.debug("START iterate projects")

logging.info("Found # of projects: "+str(projects["count"]))

for project in projects["value"]:
    #if _AUTH["skip_all_but"] not in project["name"]: continue

    logging.debug("START process project "+project["name"])

    file_path= "../../data/azure-devops_"+makeFileName(_ORGANIZATION+"_"+project["name"]+".json")

    # @TODO create arg to skip files
    #if os.path.exists(file_path):
    #    logging.info("Skipping "+file_path)
    #    continue

    logging.debug("START get wikis")

    url = 'https://dev.azure.com/'+_ORGANIZATION+'/'+project["name"]+'/_apis/wiki/wikis?api-version=5.1'
    response = requests.get(url, data={}, auth=(_AUTH["user"], _AUTH["token"]))
    response = json.loads(response.text)
    wikis = response
    #pprint(wikis)
    #sys.exit()

    logging.debug("END get wikis")

    logging.info("Found # of wikis: "+str(wikis["count"]))

    logging.debug("START iterate wikis")

    project["wikis"] = {}
    for wiki in wikis["value"]:

        logging.debug("START process wiki "+wiki["name"])

        project["wikis"][wiki["name"]] = []

        logging.debug("START get pages")
        
        #GET   https://dev.azure.com/{organization}/{project}/_apis/wiki/wikis/{wikiIdentifier}/pages?path=/SamplePage973&includeContent=True&api-version=5.1
        #if wiki["id"] != "bd54602c-e126-4c3d-ac1d-f1efdd172f53": continue
        url = 'https://dev.azure.com/'+_ORGANIZATION+'/'+project["id"]+'/_apis/wiki/wikis/'+wiki["id"]+'/pages?api-version=5.1&path=%2F&recursionLevel=120&includeContent=True&VersionControlRecursionType=full'
        response = requests.get(url, data={}, auth=(_AUTH["user"], _AUTH["token"]))
        response = json.loads(response.text)
        pages = response
        #pprint(pages)
        #sys.exit()

        logging.debug("END get pages")

        logging.info("Found # of pages: "+str(len(pages)))

        wikiAttrs = {
            "organization": _ORGANIZATION,
            "project_id": project["id"],
            "wiki_id": wiki["id"]
        }
        wikiObj = Wiki(wikiAttrs)
        wikiObj.setPages(pages)
        wikiObj.setPagesContent(pages)
        project["wikis"][wiki["name"]] = wikiObj.getPages()
        #sys.exit()

        logging.debug("END process wiki "+wiki["name"])

    logging.debug("END iterate wikis") 

    #logging.debug("START write file "+file_path)

    #pprint(resource_result)
    #project_array = []
    #project_array.append(project)
    #resource_result = json.dumps(project_array)
    #file = open(file_path,"w")  
    #file.write(resource_result)
    #file.close()

    #logging.debug("END write file "+file_path)

logging.debug("START write file "+file_path)

file_path= "../../data/azure-devops_"+makeFileName(_ORGANIZATION+".json")

resource_result = json.dumps(_WRITE_TO_FILE)
file = open(file_path,"w")  
file.write(resource_result)
file.close()

logging.debug("END write file "+file_path)