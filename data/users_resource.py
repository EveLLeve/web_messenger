from flask import jsonify
from flask_restful import Resource, abort

from . import db_session
from .user import User
from .parser_user import parser


def abort_if_news_not_found(users_id):
    session = db_session.create_session()
    user = session.query(User).get(users_id)
    if not user:
        abort(404, message=f"User {users_id} not found")


class UsersResource(Resource):
    def get(self, users_id):
        abort_if_news_not_found(users_id)
        session = db_session.create_session()
        news = session.query(User).get(users_id)
        return jsonify({'users': news.to_dict(
            only=('name', 'surname', 'age', 'position', 'speciality', 'address', 'email'))})

    def delete(self, users_id):
        abort_if_news_not_found(users_id)
        session = db_session.create_session()
        user = session.query(User).get(users_id)
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})


class UsersListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify({'users': [item.to_dict(
            only=('name', 'surname', 'age', 'position', 'speciality', 'address', 'email')) for item in users]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        news = User(
            name=args['name'],
            surname=args['surname'],
            age=args['age'],
            position=args['position'],
            speciality=args['speciality'],
            email = args['email'],
            address = args['address']
        )
        session.add(news)
        session.commit()
        return jsonify({'id': news.id})
