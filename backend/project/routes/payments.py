from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime

from project.models.base import db
from project.models.payment import Payment
from project.models.expenses import Expense, ExpenseSplit
from project.models.households import HouseholdMember

payments_bp = Blueprint('payments', __name__)


def _get_membership(household_id):
    return HouseholdMember.query.filter_by(
        user_id=current_user.id,
        household_id=household_id,
        is_active=True
    ).first()


def _serialize(p):
    return {
        'id': p.id,
        'household_id': p.household_id,
        'payer_id': p.payer_id,
        'payer_name': p.payer.name,
        'payee_id': p.payee_id,
        'payee_name': p.payee.name,
        'amount': str(p.amount),
        'note': p.note,
        'created_at': p.created_at.isoformat() if p.created_at else None,
    }


@payments_bp.route('/list', methods=['GET'])
@login_required
def list_payments():
    household_id = request.args.get('household_id', type=int)
    if not household_id:
        return jsonify({'error': 'household_id query param required'}), 400
    if not _get_membership(household_id):
        return jsonify({'error': 'Not found'}), 404

    payments = (
        Payment.query
        .filter_by(household_id=household_id)
        .order_by(Payment.created_at.desc())
        .all()
    )
    return jsonify([_serialize(p) for p in payments])


@payments_bp.route('/get/<int:payment_id>', methods=['GET'])
@login_required
def get_payment(payment_id):
    p = db.get_or_404(Payment, payment_id)
    if not _get_membership(p.household_id):
        return jsonify({'error': 'Not found'}), 404
    return jsonify(_serialize(p))


@payments_bp.route('/create', methods=['POST'])
@login_required
def create_payment():
    body = request.get_json() or {}
    for field in ('household_id', 'payee_id', 'amount'):
        if field not in body:
            return jsonify({'error': f'{field} is required'}), 400

    household_id = body['household_id']
    if not _get_membership(household_id):
        return jsonify({'error': 'Not a member of this household'}), 403

    payee_id = body['payee_id']
    if payee_id == current_user.id:
        return jsonify({'error': 'Cannot pay yourself'}), 400

    payment = Payment(
        household_id=household_id,
        payer_id=current_user.id,
        payee_id=payee_id,
        amount=body['amount'],
        note=body.get('note'),
    )
    db.session.add(payment)

    # mark unsettled splits where current_user owes the payee within this household
    unsettled_splits = (
        ExpenseSplit.query
        .join(ExpenseSplit.expense)
        .filter(
            ExpenseSplit.user_id == current_user.id,
            ExpenseSplit.is_settled == False,
            Expense.paid_by_id == payee_id,
            Expense.household_id == household_id,
            Expense.is_deleted == False,
        )
        .all()
    )
    settled_now = datetime.utcnow()
    for split in unsettled_splits:
        split.is_settled = True
        split.settled_at = settled_now

    db.session.commit()
    return jsonify(_serialize(payment)), 201


@payments_bp.route('/delete/<int:payment_id>', methods=['DELETE'])
@login_required
def delete_payment(payment_id):
    p = db.get_or_404(Payment, payment_id)
    membership = _get_membership(p.household_id)
    if not membership:
        return jsonify({'error': 'Not found'}), 404
    if p.payer_id != current_user.id and membership.role != 'admin':
        return jsonify({'error': 'Forbidden'}), 403

    db.session.delete(p)
    db.session.commit()
    return jsonify({'success': True})
