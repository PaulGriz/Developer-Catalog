from flask import Flask
from flask_restful import Api
from flask_jwt import JWT

from security import authenicate, identity
from resources.user import UserRegister
from resources.category import Category, CategoryList

app = Flask(__name__)
# Setting the App's connection to data.db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
# Disabling Tracker to Improve Server Responce Times
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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
    # Importing DB inside the if statement to prevent
    # possible circular importing issues
    from db import db
    db.init_app(app)
    app.run(debug=True)
    app.run(port=5000)
