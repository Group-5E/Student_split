from flask_login import UserMixin
from .base import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=True)
    password = db.Column(db.String(255), nullable=True)
    github_id = db.Column(db.String(255), unique=True, nullable=True)
    name = db.Column(db.String(255))

