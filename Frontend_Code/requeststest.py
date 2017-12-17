import requests
import json


def delete_item(name, category_id):
    url = "https://developer-catalog.herokuapp.com/catalog/{0}/{1}".format(category_id, name)
    payload = {'name': name}
    headers = {'content-type': 'application/json'}
    r = requests.delete(url, data=json.dumps(payload), headers=headers)
    return r

name = "Baseball"
category_id = 22
delete_item(name, category_id)



"""
def delete_category_page():
    if request.method == 'POST':
        bye_category = request.form['name']
        ApiRequests.delete_category(bye_category)
        return redirect(url_for('catalog_page'))
    return render_template('delete_category.html')


def delete_category(bye_category):
    url = "https://developer-catalog.herokuapp.com/catalog/{0}".format(bye_category)
    payload = {'name': bye_category}
    headers = {'content-type': 'application/json'}
    r = requests.delete(url, data=json.dumps(payload), headers=headers)
    return r
"""