import datetime

import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Chats(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'chats'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    chat_image = sqlalchemy.Column(sqlalchemy.String, default='static/img/group/default_group.avif')
    last_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())
    users = orm.relationship("User", secondary="users_to_chats", backref="chats")
    messages = orm.relationship("Message", back_populates='chats')
