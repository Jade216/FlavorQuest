# API: spoonacular
https://spoonacular.com/food-api

FlavorQuest

# Overview
FlavorQuest is a web application designed to help users discover and manage their favorite recipes, create weekly meal plans, maintain a personalized shopping list, and track cooking times with an integrated timer. The site leverages the Spoonacular API to fetch detailed recipe information and allows users to save and organize their daily meals.

# Features
Recipe Search and Details: Users can search for recipes based on ingredients and view detailed information, including instructions, nutrition, and equipment.
Favorite Recipes: Users can like recipes to add them to their favorites list for easy access.
Weekly Meal Plan: Users can plan their meals for the week by adding recipes to specific days and meal times.
Timer: Users can set timers to track cooking times, ensuring their recipes are cooked to perfection
Shopping List: Users can maintain a shopping list that persists across sessions, with the ability to add and remove items.
User Authentication: Secure user registration and login to save personalized data.

# User Flow
Home Page: Visitors are greeted with a search bar to find recipes.
Registration/Login: Users can register or log in to access personalized features.
Search Recipes: Users search for recipes by ingredients or keywords.
View Recipe: Detailed recipe information is displayed, with options to add to favorites or meal plans.
Manage Favorites: Users can view and remove recipes from their favorites.
Create Meal Plans: Users select recipes and assign them to specific days and meals.
Shopping List: Users add items to their shopping list.
Timer: Users can set and manage timers for their cooking needs.

# Technology Stack
Frontend: HTML, CSS, JavaScript, Bootstrap
Backend: Python, Flask, Jinja2
Database: PostgreSQL
APIs: Spoonacular API
Authentication: Flask-Login, Flask-Bcrypt
Development Tools: Flask-Migrate, Flask-DebugToolbar, dotenv

# Installation
## Prerequisites
Before setting up the project, ensure you have the following installed:

- Python 3.10+
- pip
- Virtualenv (recommended)

## Clone the Repository:
git clone https://github.com/Jade216/FlavorQuest.git
cd FlavorQuest

## Create and Activate Virtual Environment:
python3 -m venv venv
source venv/bin/activate

## Install Dependencies:
pip install -r requirements.txt

## Setup
### Environment Variables
Create a .env file in the root directory:
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your_secret_key
SQLALCHEMY_DATABASE_URI=sqlite:///flavorquest.db

### Database Migration:
flask db init
flask db migrate
flask db upgrade

## Running the Application
Start the Flask application:
flask run

## Access the application at http://127.0.0.1:5000/

# Contributing
Fork the repository, create a feature branch, commit your changes, and open a pull request.

# Project Structure:
FlavorQuest/
├── app.py # Main application file
├── requirements.txt # Dependencies
├── templates/ # HTML templates
├── static/ # Static files
├── models.py # Database models
├── forms.py # Flask forms
└── README.md # This README file
