import os

from app.models import Category, Item, User
from app import db
from flask import session as login_session
from flask import jsonify



# ---------------------------------------------------------------------- #
# ---------------------->   Database Connection   <--------------------- #
# ---------------------------------------------------------------------- #



# ---------------------------------------------------------------------- #
# --------------------->   Application Functions   <-------------------- #
# ---------------------------------------------------------------------- #


def session_user():
    if 'username' not in login_session:
        return "Not Logged"
    else:
        return '%s' % login_session["username"]


def catalogJSON():
    categories = Category.query.all()
    items = Item.query.all()
    catalog = {"Category": [c.serialize for c in categories]}
    for i in catalog["Category"]:
        r = [item.serialize for item in items if item.category_id == i['id']]
        i['items'] = r
    return jsonify(catalog)


# ---------------------------------------------------------------------- #
# ---------------------->   Category Functions   <---------------------- #
# ---------------------------------------------------------------------- #

def get_all_categories():
    categories = Category.query.all()
    return categories


def get_single_category(category_id):
    category = Category.query.filter_by(id=category_id).one()
    return category.name


def post_new_category(category_name):
    if category_name == '':
        return False
    else:
        new_category = Category(name=category_name)
        db.session.add(new_category)
        db.session.commit()
        return True


def delete_category(category_id):
    category = Category.query.filter_by(id=category_id).one()
    db.session.delete(category)
    db.session.commit()


# ---------------------------------------------------------------------- #
# ------------------------>   Item Functions   <------------------------ #
# ---------------------------------------------------------------------- #


def get_5_newest_items():
    items = Item.query.order_by(Item.id.desc()).limit(5)
    return items


def count_items(category):
    items = Item.query.filter_by(category_id=category.id).all()
    total = len(list(items))
    return total


def createItem(category_id, itemName, description, user_id):
    if itemName == '':
        return False
    else:
        newItem = Item(name=itemName, description=description,
                       category_id=category_id, user_id=user_id)
        db.session.add(newItem)
        db.session.commit()
        return True


def edit_item(category_id, item_id, newName, newDescription):
    item = Item.query.filter_by(id=item_id).one()
    if newName:
        item.name = newName
    if newDescription:
        item.description = newDescription
    if category_id:
        item.category_id = category_id
    db.session.add(item)
    db.session.commit()


def delete_item(item_id):
    item = Item.query.filter_by(id=item_id).one()
    db.session.delete(item)
    db.session.commit()


# ---------------------------------------------------------------------- #
# ------------------------>   User Functions   <------------------------ #
# ---------------------------------------------------------------------- #

def post_new_user(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    db.session.add(newUser)
    db.session.commit()
    user = User.query.filter_by(email=login_session['email']).one()
    return user.id


def get_user_email(email):
    try:
        user = User.query.filter_by(email=email).one()
        return user.id
    except BaseException:
        return None
