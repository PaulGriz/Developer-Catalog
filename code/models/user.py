import sqlite3
from db import db

# Note: id is named _id to prevent issues because "id" is a python method
# However, There is no problem using "id" in SQLAlchemy so it's used here


class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    password = db.Column(db.String(80))

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def save_to_db(self):
        # sqlite3 query translation = "INSERT INTO categories VALUES (?, ?)"
        # Inserts new data and updates excising data to db
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_username(cls, username):
        # SQLite Translation -->
        # SELECT * FROM users WHERE username=username
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_id(cls, _id):
        # SQLite Translation -->
        # SELECT * FROM users WHERE id=_id
        return cls.query.filter_by(id=_id).first()
