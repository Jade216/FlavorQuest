import os
import unittest
from app import app, db
from models import User

class AppConfigTest(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        self.app_context = app.app_context()  
        self.app_context.push()  
        self.client = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_homepage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'FlavorQuest', response.data)

    def test_register_page_access(self):
        """Test that the registration page is accessible without login."""
        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Register', response.data)

    def test_login_page_access(self):
        """Test that the login page is accessible without login."""
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)

    def test_404_page(self):
        """Test that a non-existent route returns a 404 page."""
        response = self.client.get('/nonexistentpage')
        self.assertEqual(response.status_code, 404)
    

if __name__ == "__main__":
    unittest.main()


