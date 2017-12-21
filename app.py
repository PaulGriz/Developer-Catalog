import json
import random
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
from resources.viewstesting import ApiEndpoints
from resources.helper_functions import Helpers

app = Flask(__name__, static_folder='static')
engine = create_engine('sqlite:///devshareDB.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "DevShare"

state = Helpers.create_state_token()

# API Endpoint - outputs all items by category
@app.route('/catalog/json')
def json_page():
    return ApiEndpoints.catalogJSON()


@app.route('/login/')
def login_page():
    login_session['state'] = state
    return render_template('login.html', STATE=state)

# The main categories page
# Note that `main.html` has the header, nav, etc.
# Note that each page has a `loginCheck` to see wheter the user is logged in
@app.route('/')
def showCategories():
    if 'username' in login_session:
        loginCheck = True
    else:
        loginCheck = False

    render_template('main.html', loginCheck=loginCheck)

    def changer(catId):
        category = session.query(Category).filter_by(id=catId).one()
        return category.name

    categories = session.query(Category).all()
    latestItems = session.query(Item).order_by(Item.id.desc()).limit(5)
    return render_template('index.html', 
    categories=categories,
    latestItems=latestItems,
    getLatestCatFromId=getLatestCatFromId,
    loginCheck=loginCheck,
    testCheck=testCheck,
    changer=changer,
    itemCounter=itemCounter)


@app.route('/category/<string:category_name>/delete', methods=['GET', 'POST'])
def delete_category_page(category_name):
    if 'username' not in login_session:
        loginCheck = False
        flash("You must be logged in to delete an item!", "danger")
        return redirect(url_for('showCategories'))
    elif 'username' in login_session:
        loginCheck = True
        category = session.query(Category).filter_by(name=category_name).one()
        if request.method == 'POST':

            # the user has selected no to the deletion
            if request.form['delete'] == 'no':
                return render_template('single_category.html',
                                        category=category,
                                        loginCheck=loginCheck,
                                        testCheck=testCheck,
                                        deleteQuestion=False,
                                        itemCheck=True)
            # the user has selected yes to the deletion
            if request.form['delete'] == 'yes':
                delete_category(category.id)
                flash("{0} was deleted".format(category.name), "success")
                return redirect(url_for('showCategories'))
        else:
            return render_template('single_category.html',
                                        category=category,
                                        loginCheck=loginCheck,
                                        testCheck=testCheck,
                                        deleteQuestion=True,
                                        categoryloaded=True)
    else:
        flash("Error Deleting Category!", "danger")
        return redirect(url_for('showCategories'))


# Identical to the main page, but shows catalog items based on selection
@app.route('/catalog/<string:catId>/items')
def showCatalogItems(catId):
    if 'username' in login_session:
        loginCheck = True
    else:
        loginCheck = False
    categories = session.query(Category).all()
    selectedCat = session.query(Category).filter_by(name=catId).one()
    selectedItems = session.query(Item).filter_by(
        category_id=selectedCat.id).all()
    numItems = len(selectedItems)
    return render_template('catItems.html',
                           categories=categories,
                           selectedItems=selectedItems,
                           selectedCat=selectedCat,
                           numItems=numItems,
                           loginCheck=loginCheck,
                           testCheck=testCheck,
                           itemCounter=itemCounter)


# Description
@app.route('/catalog/<string:catId>/<string:itemId>')
def showDescription(catId, itemId):
    if 'username' in login_session:
        loginCheck = True
    else:
        loginCheck = False

    itemCheck = True
    # This try block handles an edge case when thee are no items
    try:
        item = session.query(Item).filter_by(name=itemId).one()
    except BaseException:
        item = session.query(Item).filter_by(name=itemId)
        itemCount = session.query(Item).filter_by(name=itemId).count()
        if itemCount <= 0:
            itemCheck = False
    return render_template('itemDescription.html',
                           item=item,
                           loginCheck=loginCheck,
                           testCheck=testCheck,
                           deleteQuestion=False,
                           itemCheck=itemCheck)


# Add Item
@app.route('/catalog/item/new', methods=['GET', 'POST'])
def addItem():
    if 'username' in login_session:
        if request.method == 'POST':
            name = request.form['name']
            description = request.form['description']
            category = request.form['category']
            userId = getUserID(login_session["email"])

            # Check whether the name already exists
            all_categories = session.query(Item).all()
            for e in all_categories:
                if name == e.name:
                    flash(
                        '''This item name already exists.
                        Your item was not created.''',
                        "danger")
                    return redirect(url_for('showCategories'))

            # createItem() returns True if item was successfully created
            check = createItem(category, name, description, userId)
            if check is True:
                catNameAdded = session.query(
                    Category).filter_by(id=category).one()
                flash(
                    "Added %s to %s category." %
                    (name, catNameAdded.name), "success")
                return redirect(url_for('showCategories'))
            else:
                flash("Item was not created. You must include a name!",
                      "danger")
                return redirect(url_for('showCategories'))
        else:
            # if this is not a POST request and the user is logged in:
            loginCheck = True
            categories = session.query(Category).all()
            return render_template('addItem.html',
                                   loginCheck=loginCheck,
                                   categories=categories,
                                   testCheck=testCheck)
    else:
        # if the user is not logged in:
        flash("You have to be logged in to add an item!", "danger")
        return redirect(url_for('showCategories'))


# Delete Item
@app.route('/catalog/<string:itemId>/delete', methods=['GET', 'POST'])
def deleteItem(itemId):
    if 'username' not in login_session:
        loginCheck = False
        flash("You must be logged in to delete an item!", "danger")
        return redirect(url_for('showCategories'))
    elif 'username' in login_session:
        loginCheck = True
        item = session.query(Item).filter_by(name=itemId).one()
        creator = session.query(User).filter_by(id=item.user_id).one()
        if login_session['user_id'] == creator.id:
            if request.method == 'POST':
                # the first time a user clicks delete,
                # itemCheck is set to True, which will render the template
                # with a yes or no option
                if request.form['delete'] == 'maybe':
                    return render_template('itemDescription.html',
                                           item=item,
                                           loginCheck=loginCheck,
                                           testCheck=testCheck,
                                           deleteQuestion=True,
                                           itemCheck=True)
                # the user has selected no to the deletion
                if request.form['delete'] == 'no':
                    return render_template('itemDescription.html',
                                           item=item,
                                           loginCheck=loginCheck,
                                           testCheck=testCheck,
                                           deleteQuestion=False,
                                           itemCheck=True)
                # the user has selected yes to the deletion
                if request.form['delete'] == 'yes':
                    itemToDelete = session.query(
                        Item).filter_by(name=itemId).one()
                    deleteItemFunction(itemToDelete.id)
                    flash("%s was deleted" % item.name, "success")
                    return redirect(url_for('showCategories'))
        else:
            flash("You cannot delete what you did not create!", "danger")
            return redirect(url_for('showCategories'))


@app.route('/catalog/<string:itemId>/edit/', methods=['GET', 'POST'])
def editItem(itemId):
    editedItem = session.query(Item).filter_by(name=itemId).one()
    if 'username' in login_session:
        # check if user owns the item
        if editedItem.user_id != login_session['user_id']:
            flash("You can only edit the items you own!", "danger")
            return redirect(url_for('showCategories'))
        if request.method == 'POST':
            name = request.form['name']
            description = request.form['description']
            # note that this is the category id
            category = request.form['category']

            # check if name already exists
            all_categories = session.query(Item).all()
            for e in all_categories:
                if name == e.name:
                    flash(
                        '''This item name already exists.
                        Your item was not edited.''',
                        "danger")
                    return redirect(url_for('showCategories'))

            # if the name is unique, continue to edit the item
            flash("You edited %s" % editedItem.name, "info")
            editItemFunction(category, editedItem.id, name, description)
            return redirect(url_for('showCategories'))
        else:
            # if this isn't a POST request, then render the editItem template:
            loginCheck = True
            categories = session.query(Category).all()
            item = session.query(Item).filter_by(name=itemId).one()
            return render_template('editItem.html',
                                   loginCheck=loginCheck,
                                   testCheck=testCheck,
                                   categories=categories,
                                   itemId=itemId,
                                   item=item)
    else:
        flash(
            "You can only edit the items you own! Log in to proper account.",
            "danger")
        return redirect(url_for('showCategories'))


# CRUD helper functions
@app.route('/catalog/category/new', methods=['GET', 'POST'])
def post_new_category():
    if 'username' in login_session:
        if request.method == 'POST':
            name = request.form['name']
            userId = getUserID(login_session["email"])

            # Check whether the name already exists
            all_categories = session.query(Category).all()
            for category in all_categories:
                if name == category.name:
                    flash(
                        '''This Category already exists.
                        The Category was not created.''',
                        "danger")
                    return redirect(url_for('showCategories'))

            # createItem() returns True if item was successfully created
            check = post_new_category(name)
            if check is True:
                flash("{0} was successfully add.".format(name), "success")
                return redirect(url_for('showCategories'))
            else:
                flash("Category not added. Missing: New Category's Name.", "danger")
                return redirect(url_for('showCategories'))
        else:
            # if this is not a POST request and the user is logged in:
            loginCheck = True
            categories = session.query(Category).all()
            return render_template('post_category.html', loginCheck=loginCheck, categories=categories, testCheck=testCheck)
    else:
        # if the user is not logged in:
        flash("You have to be logged in to add an item!", "danger")
        return redirect(url_for('showCategories'))


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

def createItem(catId, itemName, description, userId):
    if itemName == '':
        return False
    else:
        newItem = Item(
            name=itemName,
            description=description,
            category_id=catId,
            user_id=userId)
        session.add(newItem)
        session.commit()
        return True


def editItemFunction(catId, itemId, newName, newDescription):
    item = session.query(Item).filter_by(id=itemId).one()
    if newName:
        item.name = newName
    if newDescription:
        item.description = newDescription
    if catId:
        item.category_id = catId
    session.add(item)
    session.commit()


def deleteItemFunction(itemId):
    item = session.query(Item).filter_by(id=itemId).one()
    session.delete(item)
    session.commit()


def itemCounter(category):
    items = session.query(Item).filter_by(category_id=category.id).all()
    return str(len(items))


# Login
# This function and the `login.html` template have been adapted from the
# code used in the Udacity course by Lorenzo Brown
# note that some of the comments were created by Udacity
@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.')), 401
        return response
    code = request.data

    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the authorization code.')), 401
        return response

    access_token = credentials.access_token
    url = ("https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={0}".format(access_token))
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error'))), 500
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps("Token's user ID doesn't match given user ID.")), 401
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps("Token's client ID does not match app's.")), 401
        print ("Token's client ID does not match app's.")
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.')), 200
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
    user_id = getUserID(data["email"])
    if not user_id: user_id = createUser(login_session)
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
    global loginCheck
    loginCheck = True
    return output


# Logout
# This function has been adapted from the code used in the Udacity course
# by Lorenzo Brown


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps('Current user not connected.')), 401
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
        global loginCheck
        loginCheck = False
        return redirect(url_for('showCategories'))
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.')), 400
        return response


# Helpers


def getLatestCatFromId(catId):
    cat = session.query(Category).filter_by(id=catId).one()
    return cat.name


def testCheck():
    if 'username' not in login_session:
        return "Not Logged"
    else:
        return '%s' % login_session["username"]


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except BaseException:
        return None


if __name__ == '__main__':
    app.secret_key = 'quantum_proof_password'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
