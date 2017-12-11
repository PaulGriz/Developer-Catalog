from flask_restful import Resource, reqparse
from flask_jwt import jwt_required
from models.category import CategoryModel


class Category(Resource):
    

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
        category = CategoryModel(name, data['items'])

        try:
            category.save_to_db()
        except:
            return {"message": "An error inserting the category."}, 500

        # Return data in JSON is required by Parameters in CategoryModel
        return category.json(), 201


    def delete(self, name):
        # -------------------------------------------------------------------------------
        # DELETE---> a single category
        # -------------------------------------------------------------------------------
        category = CategoryModel.find_by_name(name)

        if category:
            category.delete_from_db()

        return {'message': 'Category has been deleted'}


class CategoryList(Resource):
    def get(self):
        # Could have also used a lambda
        # --> Example: list(map(lambda x: x.json(), CategoryModel.query.all()))
        return {'categories': [category.json() for category in CategoryModel.query.all()]}
