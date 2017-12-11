from db import db


class ItemsModel(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    description = db.Column(db.String(160))

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('CategoryModel')


    def __init__(self, name, description, category_id):
        self.name = name
        self.description = description
        self.category_id = category_id

    @classmethod
    def find_by_name(cls, name):
        # Translation: SELECT * FROM categories WHERE name=name LIMIT 1
        # Pulls single category by it's name from db
        return cls.query.filter_by(name=name).first()

    def json(self):
        return {'name': self.name, 'description': self.description}

    def save_to_db(self):
        # sqlite3 query translation = "INSERT INTO categories VALUES (?, ?)"
        # Inserts new data and updates excising data to db
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
