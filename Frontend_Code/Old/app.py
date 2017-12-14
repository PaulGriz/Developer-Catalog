import os
from flask import Flask

from security import authenicate, identity
from resources.user import UserRegister
from resources.category import Category, CategoryList
from resources.items import Item, ItemList


# ------------------------------------------------------------------------------
# ---------> Flask App Setup and Configurations
# ------------------------------------------------------------------------------

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('sqlite://data.db')

# Disabling Tracker to Improve Server Responce Times
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "paulgriztest"

# ------------------------------------------------------------------------------
# ---------> End of Flask App Setup and Configurations
# ------------------------------------------------------------------------------



if __name__ == '__main__':
    # Importing DB inside the if statement to prevent circular importing
    from db import db
    db.init_app(app)
    app.run(debug=True)
    app.run(port=5000)
