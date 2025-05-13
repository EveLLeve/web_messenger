from flask import jsonify
from flask_restful import Resource, abort, reqparse

from . import db_session
from .user import User

parser = reqparse.RequestParser()
parser.add_argument('username', required=True)
parser.add_argument('name', required=True)
parser.add_argument('friends', required=True)
parser.add_argument('surname', required=True)
parser.add_argument('email', required=True)
parser.add_argument('user_id', required=True, type=int)


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    user = session.get(User, user_id)
    if not user:
        abort(404, message=f"User {user_id} not found")


class UserResource(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.get(User, user_id)
        return jsonify({'user': user.to_dict(
            only=('username', 'friends', 'user_id', 'email'))})

    def delete(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.get(User, user_id)
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})


class UserListResource(Resource):
    def get(self):
        session = db_session.create_session()
        user = session.query(User).all()
        return jsonify({'user': [item.to_dict(
            only=('username', 'friends', 'user_id', 'email')) for item in user]})
