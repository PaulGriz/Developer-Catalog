import requests


class ApiRequests():

    def get_all_category_names():
        r = requests.get("https://developer-catalog.herokuapp.com/catalog")
        data = r.json()
        categories = data['categories']
        names = []
        for category in categories:
            names.append(category['name'])
        return names

    def get_single_category(category_from_url):
        r = requests.get("https://developer-catalog.herokuapp.com/catalog/{0}".format(category_from_url))
        data = r.json()
        category_name = data['name']
        items_list = data['items']
        category_items = []
        for name in items_list:
            category_items.append(name['name'])
        return category_name, category_items

    def get_single_category_item(item_from_url):
        r = requests.get("https://developer-catalog.herokuapp.com/catalog/items/{0}".format(item_from_url))
        data = r.json()
        return data