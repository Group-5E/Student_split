from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from decimal import Decimal

from project.models.base import db
from project.models.expenses import Expense, ExpenseSplit
from project.models.households import HouseholdMember

expenses_bp = Blueprint('expenses', __name__)


def _get_membership(household_id):
    return HouseholdMember.query.filter_by(
        user_id=current_user.id,
        household_id=household_id,
        is_active=True
    ).first()


def _serialize(e):
    return {
        'id': e.id,
        'household_id': e.household_id,
        'paid_by_id': e.paid_by_id,
        'paid_by_name': e.paid_by.name,
        'description': e.description,
        'amount': str(e.amount),
        'split_type': e.split_type,
        'category': e.category,
        'notes': e.notes,
        'expense_date': e.expense_date.isoformat() if e.expense_date else None,
        'created_at': e.created_at.isoformat() if e.created_at else None,
        'splits': [
            {
                'id': s.id,
                'user_id': s.user_id,
                'username': s.user.username,
                'name': s.user.name,
                'amount_owed': str(s.amount_owed),
                'is_settled': s.is_settled,
                'settled_at': s.settled_at.isoformat() if s.settled_at else None,
            }
            for s in e.splits
        ],
    }


def _compute_splits(amount, split_type, splits_data):
    total = Decimal(str(amount))

    if split_type == 'equal':
        n = len(splits_data)
        per_person = round(total / n, 2)
        result = [(s['user_id'], per_person) for s in splits_data]
        diff = total - per_person * n
        if diff:
            result[-1] = (result[-1][0], result[-1][1] + diff)
        return result

    if split_type == 'percentage':
        result = [(s['user_id'], round(total * Decimal(str(s['percentage'])) / 100, 2)) for s in splits_data]
        diff = total - sum(r[1] for r in result)
        if diff:
            result[-1] = (result[-1][0], result[-1][1] + diff)
        return result

    if split_type == 'fixed':
        return [(s['user_id'], Decimal(str(s['amount_owed']))) for s in splits_data]

    return []


@expenses_bp.route('/list', methods=['GET'])
@login_required
def list_expenses():
    household_id = request.args.get('household_id', type=int)
    if not household_id:
        return jsonify({'error': 'household_id query param required'}), 400
    if not _get_membership(household_id):
        return jsonify({'error': 'Not found'}), 404

    expenses = (
        Expense.query
        .filter_by(household_id=household_id, is_deleted=False)
        .order_by(Expense.expense_date.desc())
        .all()
    )
    return jsonify([_serialize(e) for e in expenses])


@expenses_bp.route('/get/<int:expense_id>', methods=['GET'])
@login_required
def get_expense(expense_id):
    e = db.get_or_404(Expense, expense_id)
    if e.is_deleted or not _get_membership(e.household_id):
        return jsonify({'error': 'Not found'}), 404
    return jsonify(_serialize(e))


@expenses_bp.route('/create', methods=['POST'])
@login_required
def create_expense():
    body = request.get_json() or {}
    for field in ('household_id', 'description', 'amount', 'expense_date', 'splits'):
        if field not in body:
            return jsonify({'error': f'{field} is required'}), 400

    household_id = body['household_id']
    if not _get_membership(household_id):
        return jsonify({'error': 'Not a member of this household'}), 403

    splits_data = body['splits']
    if not splits_data:
        return jsonify({'error': 'splits cannot be empty'}), 400

    try:
        expense_date = datetime.fromisoformat(body['expense_date'])
    except ValueError:
        return jsonify({'error': 'Invalid expense_date format, use ISO 8601'}), 400

    split_type = body.get('split_type', 'equal')
    expense = Expense(
        household_id=household_id,
        paid_by_id=current_user.id,
        description=body['description'],
        amount=body['amount'],
        split_type=split_type,
        category=body.get('category', 'other'),
        notes=body.get('notes'),
        expense_date=expense_date,
    )
    db.session.add(expense)
    db.session.flush()

    for user_id, amount_owed in _compute_splits(body['amount'], split_type, splits_data):
        db.session.add(ExpenseSplit(expense_id=expense.id, user_id=user_id, amount_owed=amount_owed))

    db.session.commit()
    return jsonify(_serialize(expense)), 201


@expenses_bp.route('/update/<int:expense_id>', methods=['PUT'])
@login_required
def update_expense(expense_id):
    e = db.get_or_404(Expense, expense_id)
    if e.is_deleted:
        return jsonify({'error': 'Not found'}), 404

    membership = _get_membership(e.household_id)
    if not membership:
        return jsonify({'error': 'Not found'}), 404
    if e.paid_by_id != current_user.id and membership.role != 'admin':
        return jsonify({'error': 'Forbidden'}), 403

    body = request.get_json() or {}
    for field in ('description', 'amount', 'category', 'notes'):
        if field in body:
            setattr(e, field, body[field])
    if 'expense_date' in body:
        try:
            e.expense_date = datetime.fromisoformat(body['expense_date'])
        except ValueError:
            return jsonify({'error': 'Invalid expense_date format, use ISO 8601'}), 400

    if 'splits' in body:
        split_type = body.get('split_type', e.split_type)
        e.split_type = split_type
        for s in list(e.splits):
            db.session.delete(s)
        db.session.flush()
        for user_id, amount_owed in _compute_splits(e.amount, split_type, body['splits']):
            db.session.add(ExpenseSplit(expense_id=e.id, user_id=user_id, amount_owed=amount_owed))

    db.session.commit()
    return jsonify(_serialize(e))


@expenses_bp.route('/delete/<int:expense_id>', methods=['DELETE'])
@login_required
def delete_expense(expense_id):
    e = db.get_or_404(Expense, expense_id)
    if e.is_deleted:
        return jsonify({'error': 'Not found'}), 404

    membership = _get_membership(e.household_id)
    if not membership:
        return jsonify({'error': 'Not found'}), 404
    if e.paid_by_id != current_user.id and membership.role != 'admin':
        return jsonify({'error': 'Forbidden'}), 403

    e.is_deleted = True
    db.session.commit()
    return jsonify({'success': True})
