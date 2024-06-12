from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import UserMixin

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    db.app = app
    db.init_app(app)


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    shopping_list = db.Column(db.PickleType, default=[])

    note = db.relationship('UserNote', backref='user', uselist=False)
    meal_plans = db.relationship('WeeklyMealPlan', backref='user', lazy=True)
    favorite_recipes = db.relationship('FavoriteRecipe', backref='user', lazy=True)

class UserNote(db.Model):
    __tablename__ = 'user_notes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    notes = db.Column(db.Text, nullable=True)


class Recipe(db.Model):
    __tablename__ = 'recipe'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    nutrition = db.Column(db.Text)
    image_url = db.Column(db.String, default='https://aherousa.org/admin/fm/source/empty.png')

    meal_plans = db.relationship('WeeklyMealPlan', backref='recipe', lazy=True)
    favorite_recipes = db.relationship('FavoriteRecipe', backref='recipe', lazy=True)

class Ingredient(db.Model):
    __tablename__ = 'ingredient'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)


class RecipeIngredient(db.Model):
    __tablename__ = 'recipe_ingredient'
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.id'), nullable=False)
    quantity = db.Column(db.String)
    unit = db.Column(db.String)


class FavoriteRecipe(db.Model):
    __tablename__ = 'favorite_recipes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    recipe_name = db.Column(db.String, nullable=False)
    recipe_image_url = db.Column(db.String, nullable=True)


class WeeklyMealPlan(db.Model):
    __tablename__ = 'weeklymealplan'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    day = db.Column(db.String, nullable=False)
    meal = db.Column(db.String, nullable=False)
    

