import datetime

import sqlalchemy

from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Message(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'messages'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    chat_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("chats.id"))
    content = sqlalchemy.Column(sqlalchemy.String)
    creator = sqlalchemy.Column(sqlalchemy.String,
                                sqlalchemy.ForeignKey("users.username"))
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    user = orm.relationship("User")
    chats = orm.relationship('Chats')
