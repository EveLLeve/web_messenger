import datetime

import sqlalchemy

from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Notification(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'notifications'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    creator = sqlalchemy.Column(sqlalchemy.String)
    target = sqlalchemy.Column(sqlalchemy.String,
                               sqlalchemy.ForeignKey("users.username"))
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    user = orm.relationship("User")
