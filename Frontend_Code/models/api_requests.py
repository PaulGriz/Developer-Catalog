import requests
import json


class ApiRequests():

     #-------> Categories

    def get_all_category_names():
        r = requests.get("https://developer-catalog.herokuapp.com/catalog")
        data = r.json()
        categories = data['categories']
        names = []
        for category in categories:
            names.append(category['name'])
        return names

    def get_single_category(category_from_url):
        r = requests.get(
            "https://developer-catalog.herokuapp.com/catalog/{0}".format(category_from_url))
        data = r.json()
        category_name = data['name']
        items_list = data['items']
        category_items = []
        for name in items_list:
            category_items.append(name['name'])
        return category_name, category_items

    def post_category(new_category):
        url = "https://developer-catalog.herokuapp.com/catalog/{0}".format(
            new_category)
        payload = {'name': new_category}
        headers = {'content-type': 'application/json'}
        r = requests.post(url, data=json.dumps(payload), headers=headers)
        return r

    def delete_category(bye_category):
        url = "https://developer-catalog.herokuapp.com/catalog/{0}".format(bye_category)
        payload = {'name': bye_category}
        headers = {'content-type': 'application/json'}
        r = requests.delete(url, data=json.dumps(payload), headers=headers)
        return r

    #-------> Items

    def get_single_category_item(item_from_url):
        r = requests.get(
            "https://developer-catalog.herokuapp.com/catalog/items/{0}".format(item_from_url))
        data = r.json()
        return data

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

