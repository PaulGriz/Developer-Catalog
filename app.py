import os
from flask import Flask
from flask_restful import Api
from flask_jwt import JWT

from security import authenicate, identity
from resources.user import UserRegister
from resources.category import Category, CategoryList
from resources.items import Item, ItemList


# ------------------------------------------------------------------------------
# ---------> Flask App Setup and Configurations
# ------------------------------------------------------------------------------

app = Flask(__name__)

""" The Database is a Postgres Database hosted by Heroku
    The appliction's --> 'DATABASE_URL' is given by Heroku in the settings
    The second opion --> 'sqlite://data.db' is for local Development
    If you run the appliction locally the data.db will be created """

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite://data.db')

# Disabling Tracker to Improve Server Responce Times
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "paulgriztest"
api = Api(app)

# Adds a /auth endpoint to authenicate users
jwt = JWT(app, authenicate, identity)

# ------------------------------------------------------------------------------
# ---------> End of Flask App Setup and Configurations
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# ---------> API Endpoints
# ------------------------------------------------------------------------------
#---> Categories
api.add_resource(CategoryList, '/catalog')
api.add_resource(Category, '/catalog/<string:name>')
#---> Items
api.add_resource(ItemList, '/catalog/items')
api.add_resource(Item, '/catalog/items/<string:name>')
#---> Authentication
api.add_resource(UserRegister, '/register')

# ------------------------------------------------------------------------------
# ---------> End of API Endpoints
# ------------------------------------------------------------------------------

if __name__ == '__main__':
    # Importing DB inside the if statement to prevent circular importing
    from db import db
    db.init_app(app)
    app.run(debug=True)
    app.run(port=5000)
