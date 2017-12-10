import sqlite3
from flask_restful import Resource, reqparse
from flask_jwt import jwt_required


class CategoryList(Resource):
    def get(self):
        # -------------------------------------------------------------------------------
        # GET ---> all Categories
        # -------------------------------------------------------------------------------
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "SELECT * FROM categories"
        result = cursor.execute(query)
        categories = []
        for row in result:
            categories.append({'name': row[0], 'category_items': row[1]})
        connection.close()
        return {'categories' : categories}


class Category(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('category_items',
        type=str,
        required=True,
        help="This field cannot be left blank"
    )

    @classmethod
    def insert(cls, category):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "INSERT INTO categories VALUES (?, ?)"
        cursor.execute(query, (category['name'], category['category_items']))

        connection.commit()
        connection.close()

    @classmethod
    def find_by_name(cls, name):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "SELECT * FROM categories WHERE name=?"
        result = cursor.execute(query, (name,))
        row = result.fetchone()
        connection.close()

        if row:
            return {'category' : {'name' : row[0], 'category_items' : row[1]}}

    @classmethod
    def update(cls, category):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "UPDATE categories SET category_items=? WHERE name=?"
        cursor.execute(query, (category['category_items'], category['name']))

        connection.commit()
        connection.close()


    def get(self, name):
        # -------------------------------------------------------------------------------
        # get a single category
        # -------------------------------------------------------------------------------
        category = self.find_by_name(name)
        if category:
            return category
        return {'message' : 'Category not found'}, 404


    def post(self, name):
        # -------------------------------------------------------------------------------
        # post a new category
        # -------------------------------------------------------------------------------
        if self.find_by_name(name):
            return {'message': "A category named '{}' already exists.".format(name)}, 400

        data = Category.parser.parse_args()
        category = {'name' : name, 'category_items' : data['category_items']}

        try:
            self.insert(category)
        except:
            {"message": "An error inserting the category."}, 500

        return category, 201


    def put(self, name):
        # -------------------------------------------------------------------------------
        # PUT---> Edit a single category
        # -------------------------------------------------------------------------------
        data = Category.parser.parse_args()

        category = self.find_by_name(name)
        updated_category = {'name': name, 'category_items': data['category_items']}

        if category is None:
            try:
                self.insert(updated_category)
            except:
                return {"message": "An error inserting the category."}, 500
        else:
            try:
                self.update(updated_category)
            except:
                return {"message": "An error inserting the category."}, 500
        return updated_category


    def delete(self, name):
        # -------------------------------------------------------------------------------
        # DELETE---> a single category
        # -------------------------------------------------------------------------------
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        # Name = name from URL
        query = "DELETE FROM categories WHERE name=?"
        cursor.execute(query, (name,))

        connection.commit()
        connection.close()
        return {'message': 'Item deleted'}
