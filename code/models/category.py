import sqlite3


class CategoryModel:
    def __init__(self, name, category_items):
        self.name = name
        self.category_items = category_items

    def json(self):
        return {'name': self.name, 'category_items': self.category_items}

    @classmethod
    def find_by_name(cls, name):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "SELECT * FROM categories WHERE name=?"
        result = cursor.execute(query, (name,))
        row = result.fetchone()
        connection.close()

        if row:
            # returns row[0] to name and row[1] to category_items
            return cls(*row)

    def insert(self):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "INSERT INTO categories VALUES (?, ?)"
        cursor.execute(query, (self.name, self.category_items))

        connection.commit()
        connection.close()

    def update(self):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "UPDATE categories SET category_items=? WHERE name=?"
        cursor.execute(query, (self.category_items, self.name))

        connection.commit()
        connection.close()
