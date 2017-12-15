import requests
import json


def delete_category(bye_category):
    url = "https://developer-catalog.herokuapp.com/catalog/{0}".format(bye_category)
    payload = {'name': bye_category}
    headers = {'content-type': 'application/json'}
    r = requests.delete(url, data=json.dumps(payload), headers=headers)
    return r



def delete_category_page():
    bye_category = 'testcate3'
    delete_category(bye_category)
    return bye_category

delete_category_page()

