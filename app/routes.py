# Built in Libraries
import os
import json
import random
import string
import httplib2
import requests

# Flask Imports
from flask import session as login_session
from flask import Flask, flash, make_response, redirect, \
    render_template, request, url_for, current_app


# Google Signin Imports
from oauth2client.client import FlowExchangeError, flow_from_clientsecrets

# SQLAlchemy Imports
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

# Files From Project Imports
from config import Config
from app.resources.functions import *
from app import app
from app.models import Category, Item, User


# Assigns the Client ID used for Google OAuth Signin
CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())[
    'web']['client_id']
APPLICATION_NAME = "DevShare"


# Generated a random 32 character string. Used for Login Sessions
state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                for x in range(32))


# ---------------------------------------------------------------------- #
# ---------------------->   Database Connection   <--------------------- #
# ---------------------------------------------------------------------- #

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
metadata = MetaData(bind=engine)
session = sessionmaker(bind=engine)

# -------------------------------------------------------------- #
# --------------------->    Home Page    <---------------------- #
# -------------------------------------------------------------- #
# The permission object is True only when a user is logged in    #
# Permission is used throughout the app for CRUD operations      #
# A state token is given to all users when signed in             #
# -------------------------------------------------------------- #


@app.route('/')
def home_page():
    if 'username' not in login_session:
        permission = False
    else:
        permission = True
    categories = Category.query.all()
    newest_items = Item.query.order_by(Item.id.desc()).limit(5)

    return render_template('home.html', categories=categories,
                           newest_items=newest_items,
                           get_single_category=get_single_category,
                           permission=permission,
                           session_user=session_user,
                           count_items=count_items)


# -------------------------------------------------------- #
# ----------------->    Login Page    <------------------- #
# -------------------------------------------------------- #
# Here, the state token is loaded into the user session    #
# login_session will be used for the Google OAth API       #
# -------------------------------------------------------- #


@app.route('/login/')
def login_page():
    # Assigns the state token to the session user
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# ------------------------------------------------------------------- #
# ---------------------->   Category Pages   <----------------------- #
# ------------------------------------------------------------------- #

# -------------------------------------------------------------- #
# -------------->  Selected Category Items Page  <-------------- #
# -------------------------------------------------------------- #
# When the user selects a category, all the items are listed     #
# Items are listed by name in alphabetical order                 #
# Below the items is the option to delete the category           #
# -------------------------------------------------------------- #


@app.route('/catalog/<string:category_id>/items')
def get_category_items_page(category_id):
    if 'username' not in login_session:
        permission = False

    permission = True
    categories = Category.query.all()
    selected_category = Category.query.filter_by(name=category_id).one()
    selected_category_items = Item.query.filter_by(
        category_id=selected_category.id).all()
    number_of_items = count_items(selected_category)

    return render_template('get_category_items.html',
                           categories=categories,
                           selected_category_items=selected_category_items,
                           selected_category=selected_category,
                           number_of_items=number_of_items,
                           permission=permission)


# ---------------------------------------------------------- #
# ------------->   Post New Category Page   <--------------- #
# ---------------------------------------------------------- #
# This page allows users to post new categories              #
# Only signed in users have the permission to post content   #
# --> If a non-user navigates to this link:                  #
# ------> 1.) A message is flashed warning the user          #
# ------> 2.) User is redirected to the Home Page            #
#              <---------------------------->                #
# On successful login, the user is sent back to home page    #
# ---------------------------------------------------------- #


@app.route('/catalog/category/new', methods=['GET', 'POST'])
def post_new_category_page():
    if 'username' in login_session:
        if request.method == 'POST':
            name = request.form['name']
            user_id = get_user_email(login_session["email"])

            # Check whether the name already exists
            all_categories = Category.query.all()
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

            flash("Category not added. Needed: New Category's Name", "danger")
            return redirect(url_for('home_page'))

        # if this is not a POST request and the user is logged in:
        permission = True
        categories = Category.query.all()
        return render_template('post_category.html', permission=permission,
                               categories=categories,
                               session_user=session_user)

    flash("You have to loggin before posting content.", "danger")
    return redirect(url_for('home_page'))


# ------------------------------------------------------------- #
# --------------->   Delete Category Page   <------------------ #
# ------------------------------------------------------------- #
# Allows only signed in users to delete a selected category.    #
# Shows a form with yes and no options with the name.           #
# If no is selected, user is redirected back to home.           #
# If yes is selected, category is deleted from database.        #
# ------------------------------------------------------------- #


@app.route('/category/<string:category_name>/delete', methods=['GET', 'POST'])
def delete_category_page(category_name):
    if 'username' not in login_session:
        permission = False
        flash("You must be logged in to delete an item!", "danger")
        return redirect(url_for('home_page'))

    elif 'username' in login_session:
        permission = True
        category = Category.query.filter_by(name=category_name).one()
        if request.method == 'POST':
            if request.form['delete'] == 'no':
                return render_template('single_category.html',
                                       category=category,
                                       permission=True,
                                       session_user=session_user,
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


# ------------------------------------------------------------------ #
# ------------------>   END OF Category Pages   <------------------- #
# ------------------------------------------------------------------ #

# ------------------------------------------------------------------ #
# ------------------------>   Item Pages   <------------------------ #
# ------------------------------------------------------------------ #

# ---------------------------------------------------------- #
# --------------->    Selected Item Page    <--------------- #
# ---------------------------------------------------------- #
# Displays the title and description of selected item        #
# If user is logged in, CRUD options are available under     #
# ----> the description. Only logged in users have the       #
# ----> permission to these CRUD options.                    #
# ---------------------------------------------------------- #


@app.route('/catalog/<string:category_id>/<string:item_id>')
def get_item_page(category_id, item_id):
    if 'username' in login_session:
        permission = True
    else:
        permission = False

    item = Item.query.filter_by(name=item_id).one()
    # If used to ensure query returned an item and flashes
    #   an error if no item was found.
    if item is None:
        flash("Error finding item", "danger")
        return redirect(url_for('home_page'))

    return render_template('single_item.html', item=item,
                           permission=permission,
                           session_user=session_user,
                           deleteQuestion=False)


# -------------------------------------------------------------- #
# ------------------>   Post New Item Page   <------------------ #
# -------------------------------------------------------------- #
# --> If User is not signed in:                                  #
# ------> 1.) Message is flashed warning them to sign in         #
# ------> 2.) User redirected to Home Page                       #
#                <---------------------------->                  #
# --> If POST request is sent with an existing name in DB:       #
# ------> 1.) Message is flashed user warning of the name error  #
# ------> 2.) Page is refreshed allowing user to try again       #
#                <---------------------------->                  #
# --> If POST request is sent without a name:                    #
# ------> 1.) Message is flashed user warning of the name error  #
# ------> 2.) Page is refreshed allowing user to try again       #
#                <---------------------------->                  #
# On successful request, the user is told item was added and,    #
# ----> the user is redirected to the home page                  #
# -------------------------------------------------------------- #


@app.route('/catalog/item/new', methods=['GET', 'POST'])
def post_new_item_page():
    if 'username' in login_session:
        if request.method == 'POST':
            name = request.form['name']
            description = request.form['description']
            category = request.form['category']
            user_id = get_user_email(login_session["email"])

            all_items = Item.query.all()
            for item in all_items:
                if name == item.name:
                    flash('''An item with name {0} already exists.
                        Items names must be unique.
                        Try again with another name.'''.format(item.name),
                          "danger")
                    return redirect(url_for('post_new_item_page'))

            new_item = createItem(category, name, description, user_id)

            if new_item is True:
                owning_category = Category.query.filter_by(id=category).one()
                flash("Added {0} to {1} category.".format(
                    name, owning_category.name), "success")
                return redirect(url_for('home_page'))

            flash("Item was not created. You must include a name!",
                  "danger")
            return redirect(url_for('home_page'))

        permission = True
        categories = Category.query.all()
        return render_template('post_new_item.html',
                               permission=permission,
                               categories=categories,
                               session_user=session_user)

    flash("You have to be logged in to add an item!", "danger")
    return redirect(url_for('home_page'))


# -------------------------------------------------------------- #
# ------------------>   Delete Item Page     <------------------ #
# -------------------------------------------------------------- #
# --> If User is not signed in:                                  #
# ------> 1.) Message is flashed warning them to sign in         #
# ------> 2.) User redirected to Home Page                       #
#                <---------------------------->                  #
# This is an extension to the item description page              #
# --> If the user clicks on the delete item option:              #
# ------> 1.) A menu will appear asking the user Yes or No       #
# ------> 2.) If yes, the item is deleted and user sent to home  #
# ------> 3.) If no, the menu is hidden from item page           #
# -------------------------------------------------------------- #


@app.route('/catalog/<string:item_id>/delete', methods=['GET', 'POST'])
def delete_item_page(item_id):
    if 'username' not in login_session:
        permission = False
        flash("You must be logged in to delete an item!", "danger")
        return redirect(url_for('home_page'))

    permission = True
    item = Item.query.filter_by(name=item_id).one()
    owner = User.query.filter_by(id=item.user_id).one()

    if login_session['user_id'] == owner.id:
        if request.method == 'POST':

            if request.form['delete'] == 'delete_menu':
                return render_template('single_item.html', item=item,
                                       permission=permission,
                                       session_user=session_user,
                                       deleteQuestion=True, itemCheck=True)

            if request.form['delete'] == 'no':
                return render_template('single_item.html', item=item,
                                       permission=permission,
                                       session_user=session_user,
                                       deleteQuestion=False, itemCheck=True)

            if request.form['delete'] == 'yes':
                selected_item = Item.query.filter_by(name=item_id).one()
                delete_item(selected_item.id)
                flash("{0} was deleted".format(item.name), "success")
                return redirect(url_for('home_page'))

    flash("You cannot delete what you did not create!", "danger")
    return redirect(url_for('home_page'))


# -------------------------------------------------------------- #
# ------------------->   Edit Item Page   <--------------------- #
# -------------------------------------------------------------- #
# --> If User is not signed in:                                  #
# ------> 1.) Message is flashed warning them to sign in         #
# ------> 2.) User redirected to Home Page                       #
#                <---------------------------->                  #
# --> If User is not the author of the selected item:            #
# ------> 1.) Message is flashed warning them ownership error    #
# ------> 2.) User redirected to Home Page                       #
#                <---------------------------->                  #
# --> If User edits item name to an existing name in DB:         #
# ------> 1.) Message is flashed warning them of name error      #
# ------> 2.) Page is refreshed allowing user to try again       #
#                <---------------------------->                  #
# This is an extension to the item description page              #
# --> If the user clicks on the edit item option:                #
# ------> 1.) The user is redirected to the edit page            #
# ------> 2.) Here the item data is filled allowing easy edits   #
#                <---------------------------->                  #
# After a successful edit user is sent back to the home page     #
# -------------------------------------------------------------- #


@app.route('/catalog/<string:item_id>/edit/', methods=['GET', 'POST'])
def edit_item_page(item_id):
    selected_item = Item.query.filter_by(name=item_id).one()
    if 'username' in login_session:

        if selected_item.user_id != login_session['user_id']:
            flash("You can only edit the items you have posted.", "danger")
            return redirect(url_for('home_page'))

        if request.method == 'POST':
            name = request.form['name']
            description = request.form['description']
            category = request.form['category']

            all_items = Item.query.all()
            for item in all_items:
                if name == item.name:
                    flash('''This item with name "{0}" already exists.
                        Please try again.'''.format(item.name), "danger")
                    return redirect(url_for('edit_item_page'))

            # if the name is unique, continue to edit the item
            flash("You edited {0}".format(selected_item.name), "info")
            edit_item(category, selected_item.id, name, description)
            return redirect(url_for('home_page'))

        permission = True
        categories = Category.query.all()
        item = Item.query.filter_by(name=item_id).one()
        return render_template('edit_item.html',
                               permission=permission,
                               session_user=session_user,
                               categories=categories,
                               item_id=item_id, item=item)

    flash("Only logged in users can edit items", "danger")
    return redirect(url_for('home_page'))


# ------------------------------------------------------------------- #
# ---------------------->   END OF Item Pages   <-------------------- #
# ------------------------------------------------------------------- #


# -------------------------------------------------------------- #
# ---------------->  Google OAuth Connection  <----------------- #
# -------------------------------------------------------------- #
# ----> CREDIT: This function is heavily modeled after the code  #
# ------------> in the Udacity lessons by by Lorenzo Brown       #
# -------------------------------------------------------------- #


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
    url = ("https://www.googleapis.com/oauth2" +
           "/v1/tokeninfo?access_token={0}".format(access_token))
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
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += '''"style = "width: 115px; height: 115px;border-radius: 115px;
                -webkit-border-radius: 115px;-moz-border-radius: 115px;">'''
    flash('''Welcome {0}!
                You are now signed in.'''.format(login_session['username']),
          "success")
    print("done!")
    global permission
    permission = True
    return output


# -------------------------------------------------------------- #
# ---------------->  Google OAuth Disconnect  <----------------- #
# -------------------------------------------------------------- #
# ----> CREDIT: This function is heavily modeled after the code  #
# ------------> in the Udacity lessons by by Lorenzo Brown       #
# -------------------------------------------------------------- #


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


# -------------------------------------------------------------- #
# ----------------->  JSON Endpoint for APIs  <----------------- #
# -------------------------------------------------------------- #
# This endpoint returns all database entries into JSON format    #
# tHE JSON is printed out is stranded JSON form for API use      #
# -------------------------------------------------------------- #


@app.route('/catalog/json')
def json_page():
    return catalogJSON()
