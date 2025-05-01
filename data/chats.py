import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase

users_to_chats_table = sqlalchemy.Table(
    'users_to_chats',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('users', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('users.id')),
    sqlalchemy.Column('chats', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('chats.id'))
)


class Chats(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'chats'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    chat_image = sqlalchemy.Column(sqlalchemy.String, default='static/img/default_group.avif')
    users = orm.relationship("User", secondary="users_to_chats", backref="chats")
