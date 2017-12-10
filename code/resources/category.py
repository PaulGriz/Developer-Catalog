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
            # Return data in JSON is required by Parameters in CategoryModel
            return category.json()
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
            category.save_to_db()
        except:
            {"message": "An error inserting the category."}, 500

        # Return data in JSON is required by Parameters in CategoryModel
        return category.json(), 201


    def put(self, name):
        # -------------------------------------------------------------------------------
        # PUT---> Edit a single category
        # -------------------------------------------------------------------------------
        data = Category.parser.parse_args()

        category = CategoryModel.find_by_name(name)

        if category is None:
            # If category not found  --> then make a new category
            category = CategoryModel(name, data['category_items'])
        else:
            # If category was found --> then edit category
            category.category_items = data['category_items']

        # save_to_db from Class CategoryModel in file --> models / category.py
        category.save_to_db()

        # Return data in JSON is required by Parameters in CategoryModel
        return category.json()


    def delete(self, name):
        # -------------------------------------------------------------------------------
        # DELETE---> a single category
        # -------------------------------------------------------------------------------
        category = CategoryModel.find_by_name(name)

        if category:
            category.delete_from_db()

        return {'message': 'Category has been deleted'}
