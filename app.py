import json
import random
import os
import string
import time

import httplib2
import requests
from flask import session as login_session
from flask import (Flask, flash, jsonify, make_response, redirect,
                   render_template, request, url_for)
from oauth2client.client import FlowExchangeError, flow_from_clientsecrets
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.database_setup import Base, Category, Item, User
from resources.functions import ApiEndpoints, CategoryFunctions, ItemFunctions

app = Flask(__name__, static_folder='static')
engine = create_engine('sqlite:///devshareDB.db')
Base.metadata.bind = engine
db_session = sessionmaker(bind=engine)
session = db_session()

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())[
    'web']['client_id']
APPLICATION_NAME = "DevShare"

state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))


#-------------------#
#---  Home Page  ---#
#-------------------#


@app.route('/')
def home_page():
    if 'username' not in login_session:
        permission = False
    else:
        permission = True
    categories = CategoryFunctions.get_all_categories()
    newest_items = ItemFunctions.get_5_newest_items()

    print(state)
    return render_template('home.html', categories=categories, newest_items=newest_items,
                           get_single_category=get_single_category,
                           permission=permission,
                           session_user=session_user,
                           count_items=count_items)


#--------------------#
#---  Login Page  ---#
#--------------------#


@app.route('/login/')
def login_page():
    # Assigns the state token to the session user
    login_session['state'] = state
    return render_template('login.html', STATE=state)


#--------------------------------------------------------------#
#------------     Selected Category Items Page     ------------#
#--------------------------------------------------------------#
# When the user selects a category, all the items are listed   #
# Items are listed by name in alphabetical order               #
# Below the items is the option to delete the category         #
#--------------------------------------------------------------#


@app.route('/catalog/<string:category_id>/items')
def get_category_items_page(category_id):
    if 'username' not in login_session:
        permission = False

    permission = True
    categories = session.query(Category).all()
    selected_category = session.query(Category).filter_by(name=category_id).one()
    selected_category_items = session.query(Item).filter_by(category_id=selected_category.id).all()
    number_of_items = count_items(selected_category)
    print(number_of_items)
    return render_template('get_category_items.html',
                           categories=categories, selected_category_items=selected_category_items,
                           selected_category=selected_category, number_of_items=number_of_items,
                           permission=permission)


#----------------------------------------------------------#
#-----------         Selected Item Page         -----------#
#----------------------------------------------------------#
# Displays the title and description of selected item      #
# If user is logged in, CRUD options are available under   #
#----> the description. Only logged in users have the      #
#----> permission to these CRUD options.                   #
#----------------------------------------------------------#


@app.route('/catalog/<string:category_id>/<string:item_id>')
def get_item_page(category_id, item_id):
    if 'username' in login_session:
        permission = True
    else:
        permission = False
    
    item = session.query(Item).filter_by(name=item_id).one()
    # If used to ensure query returned an item and flashes
    #   an error if no item was found. 
    if item is None:
        flash("Error finding item", "danger")
        return redirect(url_for('home_page'))

    return render_template('single_item.html', item=item,  permission=permission,
                        session_user=session_user, deleteQuestion=False)


#----------------------------------------------------------#
#-----------      Post New Category Page        -----------#
#----------------------------------------------------------#
# ------> TODO Enter explanation for the page              #
#----------------------------------------------------------#


@app.route('/catalog/category/new', methods=['GET', 'POST'])
def post_new_category():
    if 'username' in login_session:
        if request.method == 'POST':
            name = request.form['name']
            user_id = get_user_email(login_session["email"])

            # Check whether the name already exists
            all_categories = session.query(Category).all()
            for category in all_categories:
                if name == category.name:
                    flash('''This Category already exists.
                        The Category was not created.''', "danger")
                    return redirect(url_for('home_page'))

            # createItem() returns True if item was successfully created
            check = post_new_category(name)
            if check is True:
                flash("{0} was successfully add.".format(name), "success")
                return redirect(url_for('home_page'))

            flash("Category not added. Missing: New Category's Name.", "danger")
            return redirect(url_for('home_page'))

        # if this is not a POST request and the user is logged in:
        permission = True
        categories = session.query(Category).all()
        return render_template('post_category.html', permission=permission, categories=categories, session_user=session_user)


#----------------------------------------------------------#
#-----------         Post New Item Page         -----------#
#----------------------------------------------------------#
# ------> TODO Enter explanation for the page              #
#----------------------------------------------------------#


@app.route('/catalog/item/new', methods=['GET', 'POST'])
def post_new_item_page():
    if 'username' in login_session:
        if request.method == 'POST':
            name = request.form['name']
            description = request.form['description']
            category = request.form['category']
            user_id = get_user_email(login_session["email"])

            all_items = session.query(Item).all()
            for item in all_items:
                if name == item.name:
                    flash('''This item name already exists.
                        Your item was not created.''', "danger")
                    return redirect(url_for('home_page'))

            
            new_item = createItem(category, name, description, user_id)
            if new_item is True:
                owning_category = session.query(Category).filter_by(id=category).one()
                flash("Added {0} to {1} category.".format(name, owning_category.name), "success")
                return redirect(url_for('home_page'))
            else:
                flash("Item was not created. You must include a name!",
                      "danger")
                return redirect(url_for('home_page'))
        else:
            permission = True
            categories = session.query(Category).all()
            return render_template('post_new_item.html', permission=permission, categories=categories,
                                   session_user=session_user)
    else:
        flash("You have to be logged in to add an item!", "danger")
        return redirect(url_for('home_page'))


#-------------------------------------------------------------#
#---------------    Delete Category Page    ------------------#
#------------------------------------------------------------ #
# Allows only signed in users to delete a selected category.  #
# Shows a form with yes and no options with the name.         #
# If no is selected, user is redirected back to home.         #
# If yes is selected, category is deleted from database.      #
#-------------------------------------------------------------#


@app.route('/category/<string:category_name>/delete', methods=['GET', 'POST'])
def delete_category_page(category_name):
    if 'username' not in login_session:
        permission = False
        flash("You must be logged in to delete an item!", "danger")
        return redirect(url_for('home_page'))

    elif 'username' in login_session:
        permission = True
        category = session.query(Category).filter_by(name=category_name).one()
        if request.method == 'POST':
            if request.form['delete'] == 'no':
                return render_template('single_category.html', category=category,
                                       permission=True, session_user=session_user,
                                       deleteQuestion=False, itemCheck=True)

            if request.form['delete'] == 'yes':
                delete_category(category.id)
                flash("{0} was deleted".format(category.name), "success")
                return redirect(url_for('home_page'))
        else:
            return render_template('single_category.html', category=category,
                                   permission=True, session_user=session_user,
                                   deleteQuestion=True, categoryloaded=True)

    else:
        flash("Error Deleting Category!", "danger")
        return redirect(url_for('home_page'))


#----------------------------------------------------------#
#-----------         Delete Item Page           -----------#
#----------------------------------------------------------#
# ------> TODO Enter explanation for the page              #
#----------------------------------------------------------#


@app.route('/catalog/<string:item_id>/delete', methods=['GET', 'POST'])
def delete_item_page(item_id):
    if 'username' not in login_session:
        permission = False
        flash("You must be logged in to delete an item!", "danger")
        return redirect(url_for('home_page'))

    permission = True
    item = session.query(Item).filter_by(name=item_id).one()
    owner = session.query(User).filter_by(id=item.user_id).one()

    if login_session['user_id'] == owner.id:
        if request.method == 'POST':

            if request.form['delete'] == 'delete_menu':
                return render_template('single_item.html', item=item,
                                        permission=permission, session_user=session_user,
                                        deleteQuestion=True, itemCheck=True)

            if request.form['delete'] == 'no':
                return render_template('single_item.html', item=item,
                                        permission=permission, session_user=session_user,
                                        deleteQuestion=False, itemCheck=True)

            if request.form['delete'] == 'yes':
                selected_item = session.query(Item).filter_by(name=item_id).one()
                delete_item(selected_item.id)
                flash("{0} was deleted".format(item.name), "success")
                return redirect(url_for('home_page'))

    flash("You cannot delete what you did not create!", "danger")
    return redirect(url_for('home_page'))


#----------------------------------------------------------#
#-----------          Edit Item Page            -----------#
#----------------------------------------------------------#
# ------> TODO Enter explanation for the page              #
#----------------------------------------------------------#


@app.route('/catalog/<string:item_id>/edit/', methods=['GET', 'POST'])
def edit_item_page(item_id):
    selected_item = session.query(Item).filter_by(name=item_id).one()
    if 'username' in login_session:

        if selected_item.user_id != login_session['user_id']:
            flash("You can only edit the items you own!", "danger")
            return redirect(url_for('home_page'))

        if request.method == 'POST':
            name = request.form['name']
            description = request.form['description']
            category = request.form['category']

            # check if name already exists
            all_items = session.query(Item).all()
            for item in all_items:
                if name == item.name:
                    flash(
                        '''This item name already exists.
                        Your item was not edited.''',
                        "danger")
                    return redirect(url_for('home_page'))

            # if the name is unique, continue to edit the item
            flash("You edited {0}".format(selected_item.name), "info")
            edit_item(category, selected_item.id, name, description)
            return redirect(url_for('home_page'))

        permission = True
        categories = session.query(Category).all()
        item = session.query(Item).filter_by(name=item_id).one()
        return render_template('edit_item.html', permission=permission,
                                session_user=session_user, categories=categories,
                                item_id=item_id, item=item)

    flash("You can only edit the items you own! Log in to proper account.", "danger")
    return redirect(url_for('home_page'))


    # if the user is not logged in:
    flash("You have to be logged in to add an item!", "danger")
    return redirect(url_for('home_page'))


def post_new_category(category_name):
    if category_name == '':
        return False
    else:
        new_category = Category(name=category_name)
        session.add(new_category)
        session.commit()
        return True


def delete_category(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    session.delete(category)
    session.commit()


def createItem(category_id, itemName, description, user_id):
    if itemName == '':
        return False
    else:
        newItem = Item(
            name=itemName,
            description=description,
            category_id=category_id,
            user_id=user_id)
        session.add(newItem)
        session.commit()
        return True


def edit_item(category_id, item_id, newName, newDescription):
    item = session.query(Item).filter_by(id=item_id).one()
    if newName:
        item.name = newName
    if newDescription:
        item.description = newDescription
    if category_id:
        item.category_id = category_id
    session.add(item)
    session.commit()


def delete_item(item_id):
    item = session.query(Item).filter_by(id=item_id).one()
    session.delete(item)
    session.commit()


def count_items(category):
    items = session.query(Item).filter_by(category_id=category.id).all()
    total = len(list(items))
    return total


#----------------------------------------------------------#
#-----------      Google OAuth Connection       -----------#
#----------------------------------------------------------#
# ------> TODO Enter explanation for the page              #
#----------------------------------------------------------#


# Code is modeled after lessions by Lorenzo Brown


@app.route('/gconnect', methods=['POST'])
def gconnect():
    print(state)
    if request.args.get('state') != login_session['state']:
        print("1")
        response = make_response(json.dumps('Invalid state parameter.')), 401
        return response
    code = request.data

    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        print("2")
        response = make_response(json.dumps(
            'Failed to upgrade the authorization code.')), 401
        return response

    access_token = credentials.access_token
    url = (
        "https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={0}".format(access_token))
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error'))), 500
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        print("3")
        response = make_response(json.dumps(
            "Token's user ID doesn't match given user ID.")), 401
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        print("4")
        response = make_response(json.dumps(
            "Token's client ID does not match app's.")), 401
        print("Token's client ID does not match app's.")
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.')), 200
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    # see if user exists, if not make a new user
    user_id = get_user_email(data["email"])
    if not user_id:
        user_id = post_new_user(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome,<br>'
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += '''" style = "width: 150px; height: 150px;border-radius: 150px;
                -webkit-border-radius: 150px;-moz-border-radius: 150px;">'''
    flash("you are now logged in as %s" % login_session['username'], "success")
    print("done!")
    global permission
    permission = True
    return output


#----------------------------------------------------------#
#-----------      Google OAuth Disconnect       -----------#
#----------------------------------------------------------#
# ------> TODO Enter explanation for the page              #
#----------------------------------------------------------#


# Code is modeled after lessions by Lorenzo Brown


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps(
            'Current user not connected.')), 401
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        flash("%s just logged out." % login_session['username'], "info")
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected')), 200
        global permission
        permission = False
        return redirect(url_for('home_page'))
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.')), 400
        return response


def get_single_category(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    return category.name


def session_user():
    if 'username' not in login_session:
        return "Not Logged"
    else:
        return '%s' % login_session["username"]


def post_new_user(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def get_user_email(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except BaseException:
        return None


#----------------------------------------------------------#
#-----------       JSON Endpoint for APIs       -----------#
#----------------------------------------------------------#
# ------> TODO Enter explanation for the page              #
#----------------------------------------------------------#


@app.route('/catalog/json')
def json_page():
    return ApiEndpoints.catalogJSON()


if __name__ == '__main__':
    app.secret_key = 'quantum_proof_password'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
