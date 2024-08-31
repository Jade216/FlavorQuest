import os
from flask import Flask, session, request, render_template, redirect, flash, url_for, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager, login_required, UserMixin, current_user, login_user, logout_user
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate

from forms import RegistrationForm, LoginForm, IngredientSearchForm, EditProfileForm, ShoppingListForm
from models import db, connect_db, User, WeeklyMealPlan, UserNote, Recipe, Ingredient, RecipeIngredient, FavoriteRecipe, ShoppingListItem
import requests
from dotenv import load_dotenv
from sqlalchemy.exc import IntegrityError
import logging

logging.basicConfig(level=logging.DEBUG)

load_dotenv()

app = Flask(__name__)
bcrypt = Bcrypt(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql:///flavorquest')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SPOONACULAR_API_KEY'] = os.environ.get('SPOONACULAR_API_KEY')

toolbar = DebugToolbarExtension(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

connect_db(app)
migrate = Migrate(app, db)
with app.app_context():
    db.create_all()

app.debug = True

if __name__ == '__main__':
    app.run(debug=True)

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
    if current_user.is_authenticated:
        return redirect(url_for('homepage'))

    form = RegistrationForm()
    
    if request.method == 'POST':

        if form.validate_on_submit():
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


@app.route('/logout')
def logout():
    '''perform logout'''
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', title='Profile')


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    '''show profile edit form and make the changes'''
    form = EditProfileForm()
    
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('profile'))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    return render_template('edit_profile.html', title='Edit Profile', form=form)



@app.route('/search', methods=['GET', 'POST'])
@login_required
def search_recipes():
    '''search recipes'''
    form = IngredientSearchForm()
    recipes = []

    if request.method == 'POST' and form.validate_on_submit():
        ingredients = form.ingredients.data
        res = requests.get(
            f'https://api.spoonacular.com/recipes/findByIngredients',
            params={
                'ingredients': ingredients,
                'number': 10,
                'apiKey': app.config['SPOONACULAR_API_KEY']
            }
        )
        recipes = res.json()
    
    elif request.method == 'GET':
        query = request.args.get('api_search_query')
        if query:
            res = requests.get(
                f'https://api.spoonacular.com/recipes/complexSearch',
                params={
                    'query': query,
                    'number': 10,
                    'apiKey': app.config['SPOONACULAR_API_KEY']
                }
            )
            recipes = res.json().get('results', [])

    return render_template('search_recipes.html', form=form, recipes=recipes)


@app.route('/recipes/<int:recipe_id>')
@login_required
def recipe(recipe_id):
    '''show the recipes after user search for it'''
    recipe = Recipe.query.get(recipe_id)
    recipe_data = None

    if not recipe:
        res = requests.get(f"https://api.spoonacular.com/recipes/{recipe_id}/information?apiKey={app.config['SPOONACULAR_API_KEY']}")
        if res.status_code == 200:
            recipe_data = res.json()

            recipe_name = recipe_data.get('title') 
            recipe_instructions = recipe_data.get('instructions') 
            recipe_nutrition = str(recipe_data.get('nutrition') or 'No nutrition information available.')
            recipe_image_url = recipe_data.get('image', 'https://aherousa.org/admin/fm/source/empty.png')

            if recipe_name and recipe_instructions:
                recipe = Recipe(
                    id = recipe_data['id'],
                    name = recipe_name,
                    instructions = recipe_instructions,
                    nutrition = recipe_nutrition,
                    image_url = recipe_image_url
                )
                db.session.add(recipe)
                try:
                    db.session.commit()
                except IntegrityError:
                    db.session.rollback()
                    flash('Failed to save recipe due to database integrity error.', 'danger')
                    return redirect(url_for('search_recipes'))

            else:
                flash('Recipe data is incomplete.', 'danger') 
                return redirect(url_for('search_recipes'))

        else:
            flash('Recipe not found', 'danger')
            return redirect(url_for('search_recipes'))
    else:
        # Fetch recipe details from the database
        recipe_data = {
            'id': recipe.id,
            'title': recipe.name,
            'instructions': recipe.instructions,
            'nutrition': recipe.nutrition,
            'image': recipe.image_url
        }

    analyze_res = requests.get(f"https://api.spoonacular.com/recipes/{recipe_id}/analyzedInstructions?apiKey={app.config['SPOONACULAR_API_KEY']}")
    if analyze_res.status_code == 200:
        analyze_data = analyze_res.json()
        steps = analyze_data[0]['steps'] if analyze_data else []
    else:
        steps = []

    ingredients_res = requests.get(f"https://api.spoonacular.com/recipes/{recipe_id}/information?apiKey={app.config['SPOONACULAR_API_KEY']}")
    if ingredients_res.status_code == 200:
        ingredients_data = ingredients_res.json()
        extended_ingredients = ingredients_data.get('extendedIngredients', [])
    else:
        extended_ingredients = []

    ingredients = []
    for ingredient in extended_ingredients:
        measures = ingredient.get('measures',{}).get('us',{})
        amount = measures.get('amount', 'N/A')
        unit = measures.get('unitShort', '')
        ingredients.append({
            'name': ingredient.get('originalName', 'Unknown ingredient'),
            'amount': amount,
            'unit': unit
        })

    equipment= set()
    for step in steps:
        for equip in step.get('equipment', []):
            equipment.add(equip['name'])
    equipment = list(equipment)

    servings = recipe_data.get('servings', 'N/A')

    return render_template('recipe.html', recipe=recipe, steps= steps,ingredients=ingredients, servings=servings, equipment=equipment)


@app.route('/weekly_mealplan')
@login_required
def weekly_mealplan():
    mealplan = WeeklyMealPlan.query.filter_by(user_id=current_user.id).all()
    recipes = [{'day':item.day, 'meal':item.meal, 'recipe':Recipe.query.get(item.recipe_id)} for item in mealplan]
    all_recipes = Recipe.query.all()
    user_note = UserNote.query.filter_by(user_id=current_user.id).first()
    notes = user_note.notes if user_note else ""
    return render_template('weekly_mealplan.html', recipes=recipes, all_recipes=all_recipes, notes=notes)


@app.route('/add_to_mealplan', methods=['POST'])
@login_required
def add_to_mealplan():
    day = request.form.get('day')
    meal = request.form.get('meal')
    recipe_name = request.form.get('recipe_name')
    recipe_instructions = request.form.get('recipe_instructions')
    recipe_nutrition = request.form.get('recipe_nutrition')
    file = request.files.get('recipe_image')

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        recipe_image_url = url_for('static', filename='uploads/' + filename)
    else:
        recipe_image_url = url_for('static', filename='uploads/empty.png')

    if recipe_name and recipe_instructions:
        # Create a new recipe
        new_recipe = Recipe(
            name=recipe_name,
            instructions=recipe_instructions,
            nutrition=recipe_nutrition,
            image_url=recipe_image_url
        )
        db.session.add(new_recipe)
        db.session.commit()
        # Add the new recipe to the meal plan
        mealplan_item = WeeklyMealPlan(
            user_id=current_user.id,
            recipe_id=new_recipe.id,
            day=day,
            meal=meal
        )
        db.session.add(mealplan_item)
        db.session.commit()

        flash('Recipe added to your meal plan!', 'success')
    else:
        flash('Recipe data is incomplete.', 'danger')  

    user_note = UserNote.query.filter_by(user_id=current_user.id).first()
    notes = user_note.notes if user_note else ""

    return redirect(url_for('weekly_mealplan'))


@app.route('/add_api_recipe_to_mealplan', methods=['POST'])
@login_required
def add_api_recipe_to_mealplan():
    day = request.form.get('day')
    meal = request.form.get('meal')
    recipe_id = request.form.get('recipe_id')
    # Fetch the recipe details from the API if not already in the database
    recipe = Recipe.query.get(recipe_id)
    if not recipe:
        api_key = app.config['SPOONACULAR_API_KEY']
        res = requests.get(f'https://api.spoonacular.com/recipes/{recipe_id}/information?apiKey={api_key}')
    
        if res.status_code == 200:
            recipe_data = res.json()
            recipe_name = recipe_data.get('title') 
            recipe_instructions = recipe_data.get('instructions') 
            recipe_nutrition = str(recipe_data.get('nutrition') or 'No nutrition information available.')
            recipe_image_url = recipe_data.get('image', 'https://aherousa.org/admin/fm/source/empty.png')
            
            if recipe_name and recipe_instructions: 
                recipe = Recipe(
                    id = recipe_data['id'],
                    name = recipe_name,
                    instructions = recipe_instructions,
                    nutrition = recipe_nutrition,
                    image_url = recipe_image_url
                )
                db.session.add(recipe)
                try:
                    db.session.commit()
                except IntegrityError:
                    db.session.rollback()
                    flash('Failed to save recipe due to database integrity error.', 'danger')
                    return redirect(url_for('search_recipes'))

            else:
                flash('Recipe data is incomplete.', 'danger')  
                return redirect(url_for('search_recipes'))

        else:
            flash('Recipe not found', 'danger')
            return redirect(url_for('search_recipes'))

    # Add the recipe to the meal plan
    mealplan_item = WeeklyMealPlan(
        user_id=current_user.id,
        recipe_id=recipe.id,
        day=day,
        meal=meal
    )
    db.session.add(mealplan_item)
    db.session.commit()

    flash('Recipe added to your meal plan!', 'success')

    user_note = UserNote.query.filter_by(user_id=current_user.id).first()
    notes = user_note.notes if user_note else ""

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

@app.route('/save_notes', methods=['POST'])
@login_required
def save_notes():
    notes = request.form.get('notes')
    user_note = UserNote.query.filter_by(user_id=current_user.id).first()
    if not user_note:
        user_note = UserNote(user_id=current_user.id, notes=notes)
    else:
        user_note.notes = notes
    db.session.add(user_note)
    db.session.commit()
    flash('Notes saved successfully!', 'success')
    return redirect(url_for('weekly_mealplan'))


@app.route('/timer')
@login_required
def timer():
    return render_template('timer.html', title='Timer')

# @app.route('/shopping_list', methods=['GET', 'POST'])
# @login_required
# def shopping_list():
#     form = ShoppingListForm()
#     if form.validate_on_submit():
#         item_name = form.item.data
#         if current_user.shopping_list is None:
#             current_user.shopping_list = []
#         current_user.shopping_list.append(item_name)
        
#         if 'items' not in session:
#             session['items'] = []
#         db.session.commit()
#         flash(f'"{item_name}" added to your shopping list!', 'success')
#         session['items'].append(item_name)
#         return redirect(url_for('shopping_list'))
  
#     return render_template('shopping_list.html', form=form, items=session.get('items', []))


# @app.route('/remove_item/<int:index>', methods=['POST'])
# @login_required
# def remove_item(index):
#     items = session.get('items', [])
#     if 0 <= index < len(items):
#         removed_item = items.pop(index)
#         session['items'] = items
#         flash(f'"{removed_item}" removed from your shopping list!', 'success')
#     else:
#         flash('Invalid item index.', 'danger')
#     return redirect(url_for('shopping_list'))


@app.route('/shopping_list', methods=['GET', 'POST'])
@login_required
def shopping_list():
    form = ShoppingListForm()
    if form.validate_on_submit():
        item_name = form.item.data.strip()
        if not item_name:
            flash('Item name cannot be empty.', 'warning')
            return redirect(url_for('shopping_list'))
        
        # Create a new ShoppingListItem instance
        print(current_user.id)
        new_item = ShoppingListItem(item_name=item_name, user_id=current_user.id)
        db.session.add(new_item)
        db.session.commit()
        
        flash(f'"{item_name}" added to your shopping list!', 'success')
        return redirect(url_for('shopping_list'))
    
    # Retrieve all shopping list items for the current user
    items = ShoppingListItem.query.filter_by(user_id=current_user.id).all()
    return render_template('shopping_list.html', form=form, items=items)

@app.route('/remove_item/<int:item_id>', methods=['POST'])
@login_required
def remove_item(item_id):
    item = ShoppingListItem.query.filter_by(id=item_id, user_id=current_user.id).first()
    if item:
        db.session.delete(item)
        db.session.commit()
        flash(f'"{item.item_name}" removed from your shopping list!', 'success')
    else:
        flash('Item not found or unauthorized action.', 'danger')
    return redirect(url_for('shopping_list'))



@app.route('/like_recipe/<int:recipe_id>', methods=['POST'])
@login_required
def like_recipe(recipe_id):
    recipe = Recipe.query.get(recipe_id)
    if recipe:
        favorite_recipe = FavoriteRecipe.query.filter_by(user_id=current_user.id, recipe_id=recipe_id).first()
        if not favorite_recipe:
            favorite_recipe = FavoriteRecipe(
                user_id=current_user.id,
                recipe_id=recipe.id,
                recipe_name=recipe.name,
                recipe_image_url=recipe.image_url
            )
            db.session.add(favorite_recipe)
            db.session.commit()
            flash('Recipe added to your favorites!', 'success')
        else:
            flash('Recipe is already in your favorites!', 'info')
    else:
        flash('Recipe not found', 'danger')
    return redirect(url_for('recipe', recipe_id=recipe_id))


@app.route('/favorites')
@login_required
def favorites():
    favorites = FavoriteRecipe.query.filter_by(user_id=current_user.id).all()
    return render_template('favorites.html', favorites=favorites)

@app.route('/remove_favorite/<int:favorite_id>', methods=['POST'])
@login_required
def remove_favorite(favorite_id):
    favorite = FavoriteRecipe.query.filter_by(user_id=current_user.id, id=favorite_id).first()
    if favorite and favorite.user_id == current_user.id:
        db.session.delete(favorite)
        db.session.commit()
        flash('Recipe removed from your favorites!', 'success')
    else:
        flash('Favorite not found or not authorized', 'danger')

    return redirect(url_for('favorites'))


