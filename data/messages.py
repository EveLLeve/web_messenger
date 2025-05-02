import datetime

import sqlalchemy

from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase

messages_to_chats_table = sqlalchemy.Table(
    'messages_to_chats',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('messages', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('messages.id')),
    sqlalchemy.Column('chats', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('chats.id'))
)


class Message(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'messages'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    content = sqlalchemy.Column(sqlalchemy.String)
    creator = sqlalchemy.Column(sqlalchemy.String,
                                sqlalchemy.ForeignKey("users.username"))
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    user = orm.relationship("User")
