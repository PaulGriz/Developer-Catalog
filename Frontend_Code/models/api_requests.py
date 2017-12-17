import requests
import json


class ApiRequests():

    #------------------------------------------------------------------------------------------------------
    #-----------------------> Category Requests
    #------------------------------------------------------------------------------------------------------

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

    #------------------------------------------------------------------------------------------------------
    #-----------------------> Item Requests
    #------------------------------------------------------------------------------------------------------

    def get_all_item_names():
        r = requests.get("https://developer-catalog.herokuapp.com/catalog/items")
        data = r.json()
        items = data['items']
        return items

    def get_single_category_item(category_id, item_from_url):
        r = requests.get(
            "https://developer-catalog.herokuapp.com/catalog/{0}/{1}".format(category_id, item_from_url))
        data = r.json()
        return data

    def post_new_item(name, description, category_id):
        url = "https://developer-catalog.herokuapp.com/catalog/{0}/{1}".format(category_id, name)
        payload = {'name': name, 'description': description, 'category_id': category_id}
        headers = {'content-type': 'application/json'}
        r = requests.post(url, data=json.dumps(payload), headers=headers)
        return r

    def delete_item(name, category_id):
        url = "https://developer-catalog.herokuapp.com/catalog/{0}/{1}".format(category_id, name)
        payload = {'name': name}
        headers = {'content-type': 'application/json'}
        r = requests.delete(url, data=json.dumps(payload), headers=headers)
        return r

    def edit_item(name, description, category_id):
        url = "https://developer-catalog.herokuapp.com/catalog/{0}/{1}".format(category_id, name)
        payload = {'name': name, 'description': description, 'category_id': category_id}
        headers = {'content-type': 'application/json'}
        edited = requests.put(url, data=json.dumps(payload), headers=headers)
        return edited