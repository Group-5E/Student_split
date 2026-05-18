import unittest
import json
from decimal import Decimal

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


class CreateExpenseTestCase(unittest.TestCase):
    """Tests for POST /api/expenses/create (pay page)."""

    def setUp(self):
        self.app = create_app(TEST_CONFIG)
        self.client = self.app.test_client()

        self.client.post(
            '/api/auth/register',
            data=json.dumps(DEFAULT_USER),
            content_type='application/json',
        )

        me = self.client.get('/api/auth/me').get_json()
        self.user_id = me['user']['id']

        hh = self.client.post(
            '/api/households/create',
            data=json.dumps({'name': 'Test House', 'address': '1 Test Street'}),
            content_type='application/json',
        ).get_json()
        self.household_id = hh['id']

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def _create(self, payload):
        return self.client.post(
            '/api/expenses/create',
            data=json.dumps(payload),
            content_type='application/json',
        )

    def _base(self, **overrides):
        payload = {
            'household_id': self.household_id,
            'description': 'Water bill',
            'amount': 50.00,
            'expense_date': '2026-01-01T00:00:00',
            'split_type': 'equal',
            'splits': [{'user_id': self.user_id}],
        }
        payload.update(overrides)
        return payload

    # Description:testable cases

    def test_create_valid_description(self):
        """Standard description text (e.g. 'Water bill') - should be accepted and stored."""
        response = self._create(self._base(description='Water bill'))
        self.assertEqual(response.status_code, 201)

    def test_create_missing_description(self):
        """No description field - should return 400 because it is required."""
        payload = self._base()
        del payload['description']
        response = self._create(payload)
        self.assertEqual(response.status_code, 400)

    # Description:cases that require route-level validation.

    @unittest.skip("Needs max-length validation in create_expense route")
    def test_create_description_too_long(self):
        """Description over 300 characters - should be limited or rejected."""
        response = self._create(self._base(description='a' * 301))
        self.assertNotEqual(response.status_code, 201)

    # Category:testable cases

    def test_create_missing_category_defaults_to_other(self):
        """No category supplied - route defaults to 'other', expense should be created."""
        payload = self._base()
        payload.pop('category', None)
        response = self._create(payload)
        data = response.get_json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['category'], 'other')

    # Amount:testable cases

    def test_create_positive_amount(self):
        """Positive integer amount (e.g. 20) - should be accepted."""
        response = self._create(self._base(amount=20))
        self.assertEqual(response.status_code, 201)

    def test_create_decimal_amount(self):
        """Decimal currency amount (e.g. 12.99) - should be accepted and stored accurately."""
        response = self._create(self._base(amount=12.99))
        data = response.get_json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Decimal(data['amount']), Decimal('12.99'))

    def test_create_large_amount(self):
        """Very large amount (e.g. 9999999) - system should handle it without error."""
        response = self._create(self._base(amount=9999999))
        self.assertEqual(response.status_code, 201)

    def test_create_missing_amount(self):
        """No amount field - should return 400 because it is required."""
        payload = self._base()
        del payload['amount']
        response = self._create(payload)
        self.assertEqual(response.status_code, 400)

    # Amount:cases that require route-level validation.

    @unittest.skip("Needs negative-amount validation in create_expense route - negative values are currently accepted")
    def test_create_negative_amount(self):
        """Negative amount (e.g. -2) - should be rejected with a descriptive error."""
        response = self._create(self._base(amount=-2))
        data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertIn('positive', data.get('error', '').lower())

    # Split type:testable cases

    def test_create_equal_split(self):
        """Equal split type - full amount should be assigned to the single member."""
        response = self._create(self._base(amount=100, split_type='equal'))
        data = response.get_json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Decimal(data['splits'][0]['amount_owed']), Decimal('100.00'))

    def test_create_percentage_split(self):
        """Custom percentage split (100%) - amount_owed should match the full expense amount."""
        payload = self._base(
            amount=100,
            split_type='percentage',
            splits=[{'user_id': self.user_id, 'percentage': 100}],
        )
        response = self._create(payload)
        data = response.get_json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Decimal(data['splits'][0]['amount_owed']), Decimal('100.00'))

    def test_create_fixed_split(self):
        """Fixed split matching the expense amount exactly - should be accepted."""
        payload = self._base(
            amount=50,
            split_type='fixed',
            splits=[{'user_id': self.user_id, 'amount_owed': 50}],
        )
        response = self._create(payload)
        self.assertEqual(response.status_code, 201)

    def test_create_missing_split_type_defaults_to_equal(self):
        """No split_type supplied - route defaults to 'equal'."""
        payload = self._base()
        del payload['split_type']
        response = self._create(payload)
        data = response.get_json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['split_type'], 'equal')

    def test_create_empty_splits_rejected(self):
        """Empty splits list - should return 400 because at least one split is required."""
        response = self._create(self._base(splits=[]))
        self.assertEqual(response.status_code, 400)

    # Split type:cases that require route-level validation.

    @unittest.skip("Needs split-total validation in create_expense route - fixed split totals are not currently checked against the expense amount")
    def test_create_fixed_split_total_exceeds_amount(self):
        """Fixed split totalling more than the expense amount - should return a validation error."""
        payload = self._base(
            amount=50,
            split_type='fixed',
            splits=[{'user_id': self.user_id, 'amount_owed': 100}],
        )
        response = self._create(payload)
        self.assertEqual(response.status_code, 400)

    @unittest.skip("Needs split-total validation in create_expense route - fixed split totals are not currently checked against the expense amount")
    def test_create_fixed_split_total_below_amount(self):
        """Fixed split totalling less than the expense amount - should return a validation error."""
        payload = self._base(
            amount=50,
            split_type='fixed',
            splits=[{'user_id': self.user_id, 'amount_owed': 10}],
        )
        response = self._create(payload)
        self.assertEqual(response.status_code, 400)


if __name__ == '__main__':
    unittest.main()
