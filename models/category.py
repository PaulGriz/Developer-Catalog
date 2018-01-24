from db import db


class Category(db.Model):
    __tablename__ = 'category'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship(db.User)

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