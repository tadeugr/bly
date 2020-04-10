#!/usr/bin/env python3

import requests
import sys
import subprocess
import json

def engine(action):
    if action == "run":
        command = "docker run --name search -itd -p 7700:7700 -v data.ms:/data.ms tadeugr/meilisearch:1362"
        result = subprocess.run(command.split(" "), stdout=subprocess.PIPE)
        print(result.stdout)
    if action == "stop":
        command = "docker stop search"
        result = subprocess.run(command.split(" "), stdout=subprocess.PIPE)
        print(result.stdout)
    if action == "rm":
        engine("stop")
        command = "docker rm search"
        result = subprocess.run(command.split(" "), stdout=subprocess.PIPE)
        print(result.stdout)


def index(index, action):
    if action == "create":
        url = 'http://localhost:7700/indexes'
        data = {
            "uid": index,
            "primaryKey": "movie_id"
        }
        response = requests.post(url, data=json.dumps(data))
        print(response.text)

    if action == "delete":
        url = 'http://localhost:7700/indexes/'+index
        response = requests.delete(url)
        print(response.text)

def document(index, action, json_file = None):
    if action == "add":
        url = 'http://localhost:7700/indexes/'+index+'/documents'
        data = open(json_file, 'rb')
        response = requests.post(url, data=data)
        print(response.text)

    if action == "delete":
        url = 'http://localhost:7700/indexes/'+index
        response = requests.delete(url)
        print(response.text)

if __name__ == "__main__":
    if sys.argv[1] == "engine":
        arg_action = sys.argv[2]
        engine(arg_action)

    if sys.argv[1] == "index":
        arg_action = sys.argv[2]
        arg_index = sys.argv[3]
        index(arg_index, arg_action)

    if sys.argv[1] == "document":
        arg_action = sys.argv[2]
        arg_index = sys.argv[3]
        document(index, action, json_file = None)