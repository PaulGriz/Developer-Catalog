import httplib2
import requests
import json
import random
import string
from models.database_setup import Base, Category, Item, User
from flask import session as login_session
from flask import (Flask, flash, jsonify, make_response, redirect,
                   render_template, request, url_for)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


engine = create_engine('sqlite:///devshareDB.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


class ApiEndpoints():

    def catalogJSON():
        categories = session.query(Category).all()
        items = session.query(Item).all()
        catalog = {"Category": [c.serialize for c in categories]}
        for i in catalog["Category"]:
            r = [item.serialize for item in items if item.category_id == i['id']]
            i['items'] = r
        return jsonify(catalog)
