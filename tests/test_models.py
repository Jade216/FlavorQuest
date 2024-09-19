from app import app, db
from models import User, Recipe
import unittest

class ModelTestCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        self.app_context = app.app_context()  
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()  
    def test_create_user(self):
        user = User(username='testuser', email='test@example.com', password='password123')
        db.session.add(user)
        db.session.commit()
        self.assertEqual(user.username, 'testuser')

if __name__ == "__main__":
    unittest.main()
