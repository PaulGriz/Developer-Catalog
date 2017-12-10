import sqlite3
from flask_restful import Resource, reqparse
from flask_jwt import jwt_required
from models.category import CategoryModel


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

    def get(self, name):
        # -------------------------------------------------------------------------------
        # get a single category
        # -------------------------------------------------------------------------------
        category = CategoryModel.find_by_name(name)
        if category:
            return category.json
        return {'message' : 'Category not found'}, 404


    def post(self, name):
        # -------------------------------------------------------------------------------
        # post a new category
        # -------------------------------------------------------------------------------
        if CategoryModel.find_by_name(name):
            return {'message': "A category named '{}' already exists.".format(name)}, 400

        data = Category.parser.parse_args()
        category = CategoryModel(name, data['category_items'])

        try:
            category.insert()
        except:
            {"message": "An error inserting the category."}, 500

        return category.json(), 201


    def put(self, name):
        # -------------------------------------------------------------------------------
        # PUT---> Edit a single category
        # -------------------------------------------------------------------------------
        data = Category.parser.parse_args()

        category = CategoryModel.find_by_name(name)
        updated_category = CategoryModel(name, data['category_items'])

        if category is None:
            try:
                updated_category.insert()
            except:
                return {"message": "An error inserting the category."}, 500
        else:
            try:
                updated_category.update()
            except:
                return {"message": "An error inserting the category."}, 500
        return updated_category.json()


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
