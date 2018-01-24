from db import db

# Note: id is named _id to prevent issues because "id" is a python method
# However, There is no problem using "id" in SQLAlchemy so it's used here


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False)
    picture = db.Column(db.String(250))

    def __init__(self, name, email, picture):
        self.name = name
        self.email = email
        self.picture = picture

    def save_to_db(self):
        # sqlite3 query translation = "INSERT INTO categories VALUES (?, ?)"
        # Inserts new data and updates excising data to db
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_username(cls, name):
        # SQLite Translation -->
        # SELECT * FROM users WHERE name=name
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_by_id(cls, _id):
        # SQLite Translation -->
        # SELECT * FROM users WHERE id=_id
        return cls.query.filter_by(id=_id).first()