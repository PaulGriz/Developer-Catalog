import sqlite3
from flask_restful import Resource, reqparse
from models.user import UserModel


class UserRegister(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('username',
        type=str,
        required=True,
        help="This field cannot be blank"
    )
    parser.add_argument('password',
        type=str,
        required=True,
        help="This field cannot be left blank"
    )


    def post(self):
        data = UserRegister.parser.parse_args()

        if UserModel.find_by_username(data['username']):
            return {"message": "A user with that username already exists"}, 400

        # Uses UserModel in --> models/user.py
        # Google: "keyword argument unpacking syntax" if **data is confusing
        user = UserModel(**data)
        # save_to_db is a classmethod in UserModel
        user.save_to_db()

        return {"message": "User created sccessfully."}, 201
