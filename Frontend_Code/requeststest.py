import requests
import json



def edit_item(name, description, category_id):
    url = "https://developer-catalog.herokuapp.com/catalog/{0}/{1}".format(category_id, name)
    payload = {'name': name, 'description': description, 'category_id': category_id}
    headers = {'content-type': 'application/json'}
    edited = requests.put(url, data=json.dumps(payload), headers=headers)
    return edited


name = 'iMac'
category_id = 1
description = 'Second Tests Edit'
edit_item(name, description, category_id)
"""
def get_item_data(name, category_id):
    url = "https://developer-catalog.herokuapp.com/catalog/{0}/{1}".format(category_id, name)
    payload = {'name': name, 'category_id': category_id}
    headers = {'content-type': 'application/json'}
    r = requests.get(url, data=json.dumps(payload), headers=headers)
    return r

def edit_item_page(name, category_id):
    name = name
    category_id = category_id
    r = get_item_data(name, category_id)
    data = r.json()
    new_name = 'iMacEDITED'
    new_description = "testEDITED"
    url = "https://developer-catalog.herokuapp.com/catalog/{0}/{1}".format(category_id, name)
    payload = {'name': name, 'category_id': category_id}
    headers = {'content-type': 'application/json'}
    edited = requests.put(url, data=json.dumps(payload), headers=headers)
    return edited



edit_item_page('iMac', 1)
"""