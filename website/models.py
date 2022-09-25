import math

from . import db
from sqlalchemy.orm import declarative_base, relationship, validates
from flask_login import UserMixin
from sqlalchemy.sql import func

association_table = db.Table('association', db.Model.metadata,
                             db.Column('book_id', db.Integer, db.ForeignKey('book.id')),
                             db.Column('tag_id', db.Integer, db.ForeignKey('tags.id')))


class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    # books = relationship("Book")
    books = db.relationship('Book', backref='author')  # secondary=association_table,


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    cover = db.Column(db.String(1000))
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'))
    tags = db.relationship("Tags", secondary=association_table)

    # author_name = db.Column(db.String(150), db.ForeignKey('author.name'))


class Tags(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(50))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    token = db.Column(db.String(300))
