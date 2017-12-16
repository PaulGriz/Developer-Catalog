import requests
import json   
    
    
    
    

r = requests.get("https://developer-catalog.herokuapp.com/catalog/items")
data = r.json()
items = data['items']
name = []
description = []
category_id = []
for item in items:
    name.append(item['name'])
    description.append(item['description'])
    category_id.append(item['category_id'])
print(name)
print(description)
print(category_id)

