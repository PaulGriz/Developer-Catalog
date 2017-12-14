import requests
#from models.api_requests import ApiRequests


def get_single_category_item(item_from_url):
    r = requests.get("https://developer-catalog.herokuapp.com/catalog/items/{0}".format(item_from_url))
    data = r.json()
    return data


item_from_url = 'iPhone'
data = get_single_category_item(item_from_url)
item_name = data['name']
item_description = data['description']


