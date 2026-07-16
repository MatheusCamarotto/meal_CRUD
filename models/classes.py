#nome, descrição, data/hora e se está dentro da dieta.
from database import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(80), nullable=False, unique=True)
    username = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(80), nullable=False, unique=True)
    role = db.Column(db.String(80), nullable=False, default='user')

class Meal(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text(), nullable=True)
    meal_time = db.Column(db.DateTime(), nullable=False)
    in_diet = db.Column(db.Boolean(), nullable=False)
