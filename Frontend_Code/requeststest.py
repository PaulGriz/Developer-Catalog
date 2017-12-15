import requests
import json



def get_all_item_names():
    r = requests.get("https://developer-catalog.herokuapp.com/catalog/items")
    data = r.json()
    items = data['items']
    name = []
    description = []
    for item in items:
        name.append(item['name'])
        description.append(item['description'])
    return name, description

listname = get_all_item_names()
name = listname[0]
description = listname[1]
print (name)
print (description)

"""
url = "https://developer-catalog.herokuapp.com/catalog/items"
payload = {'name': new_category}
headers = {'content-type': 'application/json'}
r = requests.post(url, data=json.dumps(payload), headers=headers)
"""