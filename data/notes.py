import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
import datetime
from .db_session import SqlAlchemyBase


class Note(SqlAlchemyBase, SerializerMixin):
    __tablename__ = "notes"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    mood = sqlalchemy.Column(sqlalchemy.Integer)
    comment = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    transaction_date = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True, default=datetime.datetime.now)

    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship('User')

