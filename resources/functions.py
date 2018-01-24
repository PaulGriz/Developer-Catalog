import os

from db import db, Category, Items, User

from flask import session as login_session
from flask import jsonify

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from config import Config


# ---------------------------------------------------------------------- #
# ---------------------->   Database Connection   <--------------------- #
# ---------------------------------------------------------------------- #

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
db.metadata.create_all(engine)
db.session = sessionmaker(bind=engine)
session = db.session()

# ---------------------------------------------------------------------- #
# --------------------->   Application Functions   <-------------------- #
# ---------------------------------------------------------------------- #


def session_user():
    if 'username' not in login_session:
        return "Not Logged"
    else:
        return '%s' % login_session["username"]


def catalogJSON():
    categories = session.query(Category).all()
    items = session.query(Item).all()
    catalog = {"Category": [c.serialize for c in categories]}
    for i in catalog["Category"]:
        r = [item.serialize for item in items if item.category_id == i['id']]
        i['items'] = r
    return jsonify(catalog)


# ---------------------------------------------------------------------- #
# ---------------------->   Category Functions   <---------------------- #
# ---------------------------------------------------------------------- #

def get_all_categories():
    categories = session.query(Category).all()
    return categories


def get_single_category(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    return category.name


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


# ---------------------------------------------------------------------- #
# ------------------------>   Item Functions   <------------------------ #
# ---------------------------------------------------------------------- #


def get_5_newest_items():
    items = session.query(Item).order_by(Item.id.desc()).limit(5)
    return items


def count_items(category):
    items = session.query(Item).filter_by(category_id=category.id).all()
    total = len(list(items))
    return total


def createItem(category_id, itemName, description, user_id):
    if itemName == '':
        return False
    else:
        newItem = Item(name=itemName, description=description,
                       category_id=category_id, user_id=user_id)
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


# ---------------------------------------------------------------------- #
# ------------------------>   User Functions   <------------------------ #
# ---------------------------------------------------------------------- #


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
