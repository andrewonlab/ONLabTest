#! /usr/bin/python
import json
import requests
url = 'http://127.0.0.1:8080/wm/onos/datagrid/add/intents/json'
headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
r = requests.post(url, data=json.dumps(s), headers = headers)