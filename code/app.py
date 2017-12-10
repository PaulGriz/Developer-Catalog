from flask import Flask
from flask_restful import Api
from flask_jwt import JWT
from security import authenicate, identity

from resources.user import UserRegister
from resources.category import Category, CategoryList

""" Check Documentation.txt for comments too long to fit within program.
Comments will be in format ---> "Doc--[file name]--[Comment ID]"
Example ---> Doc--app.py--1 """

app = Flask(__name__)
app.secret_key = "paulgriztest"
api = Api(app)

# Adds a /auth endpoint to authenicate users
jwt = JWT(app, authenicate, identity)

# ------------------------------------------------------------------------------
# 1.) GET All Categories --> /catalog
api.add_resource(CategoryList, '/catalog')

# 2.) GET 1 SINGLE Category --> /catalog/<string:name>
api.add_resource(Category, '/catalog/<string:name>')

# 3.) Allow user's to UserRegister
api.add_resource(UserRegister, '/register')
# ------------------------------------------------------------------------------


if __name__ == '__main__':
    app.run(debug=True)
    app.run(port=5000)
