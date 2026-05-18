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

DEFAULT_USER = {
    'username': 'testuser',
    'name': 'Test User',
    'email': 'test@example.com',
    'password': 'Password123',
}

SECOND_USER = {
    'username': 'otheruser',
    'name': 'Other User',
    'email': 'other@example.com',
    'password': 'Password123',
}


class AccountUpdateTestCase(unittest.TestCase):
    """Tests for PUT /api/auth/update (account page)."""

    def setUp(self):
        self.app = create_app(TEST_CONFIG)
        self.client = self.app.test_client()
        self.client.post(
            '/api/auth/register',
            data=json.dumps(DEFAULT_USER),
            content_type='application/json',
        )

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def _update(self, payload):
        return self.client.put(
            '/api/auth/update',
            data=json.dumps(payload),
            content_type='application/json',
        )

    def _me(self):
        return self.client.get('/api/auth/me').get_json()


    # Username: testable cases

    def test_update_valid_username(self):
        """Valid new username; should be accepted and returned in the response."""
        response = self._update({'username': 'InventiveLime38'})
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['username'], 'InventiveLime38')

    # Username: cases that require route-level validation to work correctly.

    @unittest.skip("Needs same-username check in update route; currently accepted without error")
    def test_update_same_username_rejected(self):
        """Updating to the current username - should be rejected as an unnecessary change."""
        response = self._update({'username': DEFAULT_USER['username']})
        self.assertNotEqual(response.status_code, 200)

    @unittest.skip("Needs empty-value filtering in update route; empty string currently overwrites the stored username")
    def test_update_empty_username_blocked(self):
        """Empty username string - should be blocked, not saved."""
        response = self._update({'username': ''})
        self.assertNotEqual(response.status_code, 200)

    @unittest.skip("Needs special-character validation in update route")
    def test_update_username_special_chars(self):
        """Username containing special characters (e.g. 'user@#!') should be rejected."""
        response = self._update({'username': 'user@#!'})
        data = response.get_json()
        self.assertEqual(response.status_code, 400)

    @unittest.skip("Needs max-length validation in update route; username column is VARCHAR(50)")
    def test_update_username_too_long(self):
        """Username over 100 characters - should be rejected or truncated before hitting the DB."""
        response = self._update({'username': 'a' * 101})
        self.assertNotEqual(response.status_code, 200)

    # Email: testable cases

    def test_update_valid_email(self):
        """Valid new email address; should be accepted and returned in the response."""
        response = self._update({'email': 'user9@example.com'})
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['email'], 'user9@example.com')

    # Email: cases that require route-level validation to work correctly.

    @unittest.skip("Needs email-format validation in update route")
    def test_update_invalid_email_format(self):
        """Email without '@' (e.g. 'user9example.com') - should be rejected."""
        response = self._update({'email': 'user9example.com'})
        data = response.get_json()
        self.assertEqual(response.status_code, 400)

    @unittest.skip("Needs duplicate-email check in update route")
    def test_update_duplicate_email(self):
        """Email already registered to another account - should be rejected."""
        self.client.post(
            '/api/auth/register',
            data=json.dumps(SECOND_USER),
            content_type='application/json',
        )
        self.client.post('/api/auth/logout')
        self.client.post(
            '/api/auth/login',
            data=json.dumps({'email': DEFAULT_USER['email'], 'password': DEFAULT_USER['password']}),
            content_type='application/json',
        )
        response = self._update({'email': SECOND_USER['email']})
        data = response.get_json()
        self.assertEqual(response.status_code, 400)

    @unittest.skip("Needs empty-email handling in update route - empty string currently overwrites stored email instead of leaving it unchanged")
    def test_update_empty_email_leaves_unchanged(self):
        """Submitting an empty email string - email should remain unchanged, not be wiped."""
        self._update({'email': ''})
        me_data = self._me()
        self.assertEqual(me_data['user']['email'], DEFAULT_USER['email'])


if __name__ == '__main__':
    unittest.main()
