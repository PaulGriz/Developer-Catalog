from db import db


class CategoryModel(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    category_items = db.Column(db.String(80))

    def __init__(self, name, category_items):
        self.name = name
        self.category_items = category_items

    @classmethod
    def find_by_name(cls, name):
        # Translation: SELECT * FROM categories WHERE name=name LIMIT 1
        # Pulls single category by it's name from db
        return cls.query.filter_by(name=name).first()

    def json(self):
        return {'name': self.name, 'category_items': self.category_items}

    def save_to_db(self):
        # sqlite3 query translation = "INSERT INTO categories VALUES (?, ?)"
        # Inserts new data and updates excising data to db
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
