from app import app
from forms import RegistrationForm, LoginForm
import unittest

class FormTestCase(unittest.TestCase):

    def setUp(self):
        self.app_context = app.app_context()  
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop() 

    def test_valid_registration_form(self):
        form = RegistrationForm(data={
            'username': "testuser",
            'email': "test@example.com",
            'password': "password",
            'confirm_password': "password"
        })
        self.assertTrue(form.validate())

    def test_invalid_email_registration(self):
        form = RegistrationForm(data={
            'username': "testuser",
            'email': "invalid-email",
            'password': "password",
            'confirm_password': "password"
        })
        self.assertFalse(form.validate())

    def test_valid_login_form(self):
        form = LoginForm(data={
            'email': "test@example.com",
            'password': "password"
        })
        self.assertTrue(form.validate())

    def test_invalid_email_login_form(self):
        form = LoginForm(data={
            'email': "invalid-email",
            'password': "password"
        })
        self.assertFalse(form.validate())

    def test_missing_password_login_form(self):
        form = LoginForm(data={
            'email': "test@example.com",
            'password': ""
        })
        self.assertFalse(form.validate())

if __name__ == "__main__":
    unittest.main()
