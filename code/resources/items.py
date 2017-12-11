from flask_restful import Resource, reqparse
from flask_jwt import jwt_required
from models.items import ItemsModel


class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('description',
        type=str,
        required=True,
        help="Every Item needs a description"
    )
    parser.add_argument('category_id',
        type=int,
        required=True,
        help="Every item needs a category_id."
    )

    def get(self, name):
        item = ItemsModel.find_by_name(name)
        if item:
            return item.json()
        return {'message': 'Item not found'}, 404

    def post(self, name):
        if ItemsModel.find_by_name(name):
            return {'message': "An item with name '{}' already exists.".format(name)}, 400

        data = Item.parser.parse_args()
        item = ItemsModel(name, data['description'], data['category_id'])

        try:
            item.save_to_db()
        except:
            return {"message": "An error occurred inserting the item."}, 500

        return item.json(), 201

    def put(self, name):
        data = Item.parser.parse_args()
        item = ItemsModel.find_by_name(name)

        if item is None:
            item = ItemsModel(name, data['description'], data['category_id'])
        else:
            item.description = data['description']

        item.save_to_db()
        return item.json()

    def delete(self, name):
        item = ItemsModel.find_by_name(name)
        
        if item:
            item.delete_from_db()

        return {'message': 'Item deleted'}


class ItemList(Resource):
    def get(self):
        return {'items': list(map(lambda x: x.json(), ItemsModel.query.all()))}
