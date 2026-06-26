#nome, descrição, data/hora e se está dentro da dieta.
from database import db
from flask_login import UserMixin

class User(db.model, UserMixin):
    id = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(80), nullable=False, unique=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(80), nullable=False, default='user')
