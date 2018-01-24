from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Category(db.Model):
    __tablename__ = 'category'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('user')

    def __init__(self, name):
        self.name = name

    def json(self):
        # lazy='dynamic' improves the speed of creating a category
        # However, it slows down the json get all items method
        return {'id': self.id, 'name': self.name, 'user': self.user}

    @property
    def serialize(self):
        return {'name': self.name,
                'id': self.id}

    @classmethod
    def find_by_name(cls, name):
        # Translation: SELECT * FROM categories WHERE name=name LIMIT 1
        # Pulls single category by it's name from db
        return cls.query.filter_by(name=name).first()

    def save_to_db(self):
        # sqlite3 query translation = "INSERT INTO categories VALUES (?, ?)"
        # Inserts new data and updates excising data to db
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()


class Item(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    description = db.Column(db.String(160))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('user')

    @property
    def serialize(self):
        return {'name': self.name,
                'id': self.id,
                'description': self.description}

    def __init__(self, name, description, category_id, user_id):
        self.name = name
        self.description = description
        self.category_id = category_id
        self.user_id = user_id

    def json(self):
        return {
        'name': self.name,
        'description': self.description,
        'category_id': self.category_id
        }

    @classmethod
    def find_by_name(cls, name):
        # Translation: SELECT * FROM categories WHERE name=name LIMIT 1
        # Pulls single category by it's name from db
        return cls.query.filter_by(name=name).first()

    def save_to_db(self):
        # sqlite3 query translation = "INSERT INTO categories VALUES (?, ?)"
        # Inserts new data and updates excising data to db
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()


class User(db.Model):
    __tablename__ = 'user'

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