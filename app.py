import os
from flask import Flask, request, render_template, redirect, flash, url_for
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager, login_required, UserMixin, current_user, login_user, logout_user
from flask_bcrypt import Bcrypt

from forms import RegistrationForm, LoginForm, IngredientSearchForm
from models import db, connect_db, User, WeeklyMealPlan, Recipe, Ingredient, RecipeIngredient, UserPreference, FavoriteRecipe
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql:///flavorquest')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SPOONACULAR_API_KEY'] = os.environ.get('SPOONACULAR_API_KEY')

toolbar = DebugToolbarExtension(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

connect_db(app)
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def homepage():
    '''homepage'''
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    '''user registration page'''
    print("Entered /register route")
    print("Request method:", request.method) 
    if current_user.is_authenticated:
        print("User is already authenticated")
        return redirect(url_for('homepage'))

    form = RegistrationForm()
    
    if request.method == 'POST':
        print('Form data received:', request.form)

    if form.validate_on_submit():
        print("Form is validated")
        hashed_pass = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(
            username = form.username.data,
            email = form.email.data,
            password = hashed_pass
        )
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))

    else:
        print("Form errors:", form.errors)

    print("Rendering register.html with form")
    return render_template('register.html', form=form, title='Register')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('homepage'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=True)
            return redirect(url_for('homepage'))
        else:
            flash('Wrong email or password, Please try again!', 'danger')

    return render_template('login.html', form=form, title='login')


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', title='Profile')


@app.route('/search', methods=['GET', 'POST'])
@login_required
def search_recipes():
    '''search recipes'''
    form = IngredientSearchForm()

    if form.validate_on_submit():
        ingredients = form.ingredients.data
        res = request.get(
            f'https://api.spoonacular.com/recipes/findByIngredients',
            params={
                'ingredients': ingredients,
                'number': 10,
                'apiKey': Config.SPOONACULAR_API_KEY
            }
        )
        recipes = res.json()
        return render_template('recipe_list.html', recipes=recipes)

    return render_template('search_recipes.html', form=form)


@app.route('/recipes/<int:recipe_id>')
@login_required
def recipe(recipe_id):
    res = requests.get(f'https://api.spoonacular.com/recipes/{recipe_id}/information?apiKey={Config.SPOONACULAR_API_KEY}')
    recipe = res.json()
    return render_template('recipe.html', recipe=recipe)


@app.route('/weekly_mealplan')
@login_required
def weekly_mealplan():
    mealplan = WeeklyMealPlan.query.filter_by(user_id=current_user.id).all()
    recipes = [Recipe.query.get(item.recipe_id) for item in mealplan]
    return render_template('weekly_mealplan.html', recipes=recipes)


@app.route('/add_to_mealplan/<int:recipe_id>', methods=['POST'])
@login_required
def add_to_mealplan(recipe_id):
    mealplan_item = WeeklyMealPlan(
        user_id = current_user.id,
        recipe_id = recipe_id
    )
    db.session.add(mealplan_item)
    db.session.commit()
    flash('Recipe added to your meal plan!', 'success')
    return redirect(url_for('weekly_mealplan'))


@app.route('/remove_from_mealplan/<int:recipe_id>', methods=['POST'])
@login_required
def remove_from_mealplan(recipe_id):
    mealplan_item = WeeklyMealPlan.query.filter_by(
        user_id=current_user.id, recipe_id=recipe_id).first()
    db.session.delete(mealplan_item)
    db.session.commit()
    flash('Recipe removed from your meal plan!', 'success')
    return redirect(url_for('weekly_mealplan'))