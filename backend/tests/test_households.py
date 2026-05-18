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


class CreateHouseholdTestCase(unittest.TestCase):
    """Tests for POST /api/households/create."""

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

    def _create(self, payload):
        return self.client.post(
            '/api/households/create',
            data=json.dumps(payload),
            content_type='application/json',
        )

    # Testable cases

    def test_create_valid_name_only(self):
        """Valid household name with no address - household should be created."""
        response = self._create({'name': "Davina's Home"})
        data = response.get_json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['name'], "Davina's Home")

    def test_create_valid_name_and_address(self):
        """Valid name and standard UK address - both should be saved correctly."""
        response = self._create({'name': 'Test House', 'address': '12 Example Street, Portsmouth, PO1 1AA'})
        data = response.get_json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['address'], '12 Example Street, Portsmouth, PO1 1AA')

    def test_create_missing_name(self):
        """No name field in payload - should return 400 with a name-required error."""
        response = self._create({'address': '12 Example Street'})
        data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertIn('name', data.get('error', '').lower())

    def test_create_empty_name(self):
        """Empty string name - should return 400 because name is falsy."""
        response = self._create({'name': '', 'address': '12 Example Street'})
        data = response.get_json()
        self.assertEqual(response.status_code, 400)

    def test_create_sql_injection_name(self):
        """SQL injection string in household name - SQLAlchemy parameterises queries so no DB
        error should be exposed; confirms the endpoint is safe."""
        response = self._create({'name': "' OR 1=1 --", 'address': 'test'})
        self.assertNotEqual(response.status_code, 500)

    # Cases that require route-level input validation to work correctly.

    @unittest.skip("Needs special-character validation in create_household route")
    def test_create_invalid_name_special_chars(self):
        """Household name containing only special characters (e.g. 's#$$%$') - should be rejected."""
        response = self._create({'name': 's#$$%$'})
        data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertIn('invalid', data.get('error', '').lower())

    @unittest.skip("Needs address to be a required field - route currently treats it as optional")
    def test_create_missing_address(self):
        """Missing address field - should return a field error."""
        response = self._create({'name': 'Test House'})
        data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertIn('address', data.get('error', '').lower())

    @unittest.skip("Needs address format validation in create_household route")
    def test_create_invalid_address_format(self):
        """Nonsense address string (e.g. '!$#$#!@#') - should be rejected or sanitised."""
        response = self._create({'name': 'Test House', 'address': '!$#$#!@#!$!#!@#$#@!'})
        data = response.get_json()
        self.assertNotEqual(response.status_code, 201)


if __name__ == '__main__':
    unittest.main()
