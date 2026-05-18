import unittest
import json

from project import create_app
from project.models.base import db


TEST_CONFIG = {
    'TESTING': True,
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
    'SECRET_KEY': 'test-secret-key',
    'WTF_CSRF_ENABLED': False,
}

REGISTER_PAYLOAD = {
    'username': 'testuser',
    'name': 'Test User',
    'email': 'test@example.com',
    'password': 'password123',
}


class AuthRoutesTestCase(unittest.TestCase):
    """Test suite for /api/auth routes."""

    def setUp(self):
        """Create the Flask app with an in-memory SQLite database and a test client."""
        self.app = create_app(TEST_CONFIG)
        self.client = self.app.test_client()

    def tearDown(self):
        """Remove the database session and drop all tables after each test."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    # ------------------------------------------------------------------
    # Helper
    # ------------------------------------------------------------------

    def _register(self, payload=None):
        """POST /api/auth/register with the given (or default) payload."""
        if payload is None:
            payload = REGISTER_PAYLOAD
        return self.client.post(
            '/api/auth/register',
            data=json.dumps(payload),
            content_type='application/json',
        )

    def _logout(self):
        """POST /api/auth/logout."""
        return self.client.post('/api/auth/logout')

    def _login(self, email, password):
        """POST /api/auth/login with the given credentials."""
        return self.client.post(
            '/api/auth/login',
            data=json.dumps({'email': email, 'password': password}),
            content_type='application/json',
        )

    # ------------------------------------------------------------------
    # Tests
    # ------------------------------------------------------------------

    def test_register_success(self):
        """Registering with valid, unique data should return 200 and success=True."""
        response = self._register()
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])

    def test_register_duplicate_email(self):
        """Registering twice with the same email should return 400 and an error message."""
        self._register()
        response = self._register()  # same email second time
        data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['error'], 'Email already in use')

    def test_login_success(self):
        """Logging in with correct credentials after registering should return 200 and success=True."""
        self._register()
        self._logout()
        response = self._login('test@example.com', 'password123')
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])

    def test_login_wrong_password(self):
        """Logging in with the wrong password should return 401 and 'Invalid credentials'."""
        self._register()
        self._logout()
        response = self._login('test@example.com', 'wrongpassword')
        data = response.get_json()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(data['error'], 'Invalid credentials')

    def test_login_user_not_found(self):
        """Logging in with an email that doesn't exist should return 401 and 'user not found'."""
        response = self._login('nobody@example.com', 'password123')
        data = response.get_json()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(data['error'], 'user not found')

    def test_logout_success(self):
        """Logging out while authenticated should return 200 and success=True."""
        self._register()  # register also logs the user in
        response = self._logout()
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])

    def test_me_logged_in(self):
        """GET /me while logged in should return the current user's details."""
        self._register()
        response = self.client.get('/api/auth/me')
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(data['user'])
        self.assertEqual(data['user']['email'], 'test@example.com')

    def test_me_logged_out(self):
        """GET /me while not logged in should return user=None."""
        response = self.client.get('/api/auth/me')
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(data['user'])


if __name__ == '__main__':
    unittest.main()
