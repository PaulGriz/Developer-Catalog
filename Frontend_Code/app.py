import requests
from flask import Flask, render_template, request, redirect, url_for
from flask import jsonify, flash, Response
from models.api_requests import ApiRequests


app = Flask(__name__)
app.secret_key = 'development key'


@app.route('/')
def home_page():
    return render_template('home.html')


@app.route('/catalog')
def catalog_page():
    categories = ApiRequests.get_all_category_names()
    return render_template('catalog.html', categories=categories)


@app.route('/catalog/<string:category_from_url>/')
def single_category_page(category_from_url):
    category = ApiRequests.get_single_category(category_from_url)
    category_name = category[0]
    category_items = category[1]
    return render_template('single_category.html', category_name=category_name, category_items=category_items)


@app.route('/catalog/items/<string:item_from_url>')
def single_category_item_page(item_from_url):
    data = ApiRequests.get_single_category_item(item_from_url)
    item_name = data['name']
    item_description = data['description']
    return render_template('single_category_item.html', item_name=item_name, item_description=item_description)


@app.route('/catalog/new', methods=['GET', 'POST'])
def post_new_category():
    if request.method == 'POST':
        new_category = request.form['name']
        ApiRequests.post_category(new_category)
        return redirect(url_for('home_page'))
    return render_template('post_new_category.html')

@app.route('/about')
def about_page():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True)
    app.run(port=5000)
