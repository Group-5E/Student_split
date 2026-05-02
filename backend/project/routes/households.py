from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime

from project.models.base import db
from project.models.households import Household, HouseholdMember
from project.models.users import User

households_bp = Blueprint('households', __name__)


def _get_membership(household_id):
    return HouseholdMember.query.filter_by(
        user_id=current_user.id,
        household_id=household_id,
        is_active=True
    ).first()


@households_bp.route('/list', methods=['GET'])
@login_required
def list_households():
    memberships = HouseholdMember.query.filter_by(user_id=current_user.id, is_active=True).all()
    result = []
    for m in memberships:
        h = m.household
        if not h.is_active:
            continue
        result.append({
            'id': h.id,
            'name': h.name,
            'address': h.address,
            'created_at': h.created_at.isoformat() if h.created_at else None,
            'role': m.role,
            'member_count': sum(1 for mem in h.members if mem.is_active),
        })
    return jsonify(result)


@households_bp.route('/create', methods=['POST'])
@login_required
def create_household():
    body = request.get_json()
    if not body or not body.get('name'):
        return jsonify({'error': 'name is required'}), 400

    household = Household(
        name=body['name'],
        address=body.get('address'),
        created_by=current_user.id,
    )
    db.session.add(household)
    db.session.flush()

    membership = HouseholdMember(
        user_id=current_user.id,
        household_id=household.id,
        role='admin',
    )
    db.session.add(membership)
    db.session.commit()

    return jsonify({
        'id': household.id,
        'name': household.name,
        'address': household.address,
        'created_at': household.created_at.isoformat() if household.created_at else None,
        'role': 'admin',
    }), 201


@households_bp.route('/get/<int:household_id>', methods=['GET'])
@login_required
def get_household(household_id):
    membership = _get_membership(household_id)
    if not membership:
        return jsonify({'error': 'Not found'}), 404

    h = membership.household
    if not h.is_active:
        return jsonify({'error': 'Not found'}), 404

    return jsonify({
        'id': h.id,
        'name': h.name,
        'address': h.address,
        'created_at': h.created_at.isoformat() if h.created_at else None,
        'created_by': h.created_by,
        'members': [
            {
                'user_id': m.user_id,
                'username': m.user.username,
                'name': m.user.name,
                'role': m.role,
                'joined_at': m.joined_at.isoformat() if m.joined_at else None,
            }
            for m in h.members if m.is_active
        ],
    })


@households_bp.route('/update/<int:household_id>', methods=['PUT'])
@login_required
def update_household(household_id):
    membership = _get_membership(household_id)
    if not membership or membership.role != 'admin':
        return jsonify({'error': 'Forbidden'}), 403

    h = membership.household
    if not h.is_active:
        return jsonify({'error': 'Not found'}), 404

    body = request.get_json() or {}
    if 'name' in body:
        h.name = body['name']
    if 'address' in body:
        h.address = body['address']
    db.session.commit()

    return jsonify({'id': h.id, 'name': h.name, 'address': h.address})


@households_bp.route('/delete/<int:household_id>', methods=['DELETE'])
@login_required
def delete_household(household_id):
    membership = _get_membership(household_id)
    if not membership or membership.role != 'admin':
        return jsonify({'error': 'Forbidden'}), 403

    membership.household.is_active = False
    db.session.commit()
    return jsonify({'success': True})


@households_bp.route('/<int:household_id>/members/list', methods=['GET'])
@login_required
def list_members(household_id):
    if not _get_membership(household_id):
        return jsonify({'error': 'Not found'}), 404

    members = HouseholdMember.query.filter_by(household_id=household_id, is_active=True).all()
    return jsonify([
        {
            'user_id': m.user_id,
            'username': m.user.username,
            'name': m.user.name,
            'role': m.role,
            'joined_at': m.joined_at.isoformat() if m.joined_at else None,
        }
        for m in members
    ])


@households_bp.route('/<int:household_id>/members/add', methods=['POST'])
@login_required
def add_member(household_id):
    membership = _get_membership(household_id)
    if not membership or membership.role != 'admin':
        return jsonify({'error': 'Forbidden'}), 403

    body = request.get_json() or {}
    user = None
    if 'user_id' in body:
        user = db.session.get(User, body['user_id'])
    elif 'username' in body:
        user = User.query.filter_by(username=body['username']).first()
    elif 'email' in body:
        user = User.query.filter_by(email=body['email']).first()

    if not user:
        return jsonify({'error': 'User not found'}), 404

    existing = HouseholdMember.query.filter_by(user_id=user.id, household_id=household_id).first()
    if existing:
        if existing.is_active:
            return jsonify({'error': 'User is already a member'}), 409
        existing.is_active = True
        existing.left_at = None
        db.session.commit()
        return jsonify({'success': True, 'user_id': user.id, 'role': existing.role})

    new_member = HouseholdMember(
        user_id=user.id,
        household_id=household_id,
        role=body.get('role', 'member'),
    )
    db.session.add(new_member)
    db.session.commit()
    return jsonify({'success': True, 'user_id': user.id, 'role': new_member.role}), 201


@households_bp.route('/<int:household_id>/members/remove/<int:user_id>', methods=['DELETE'])
@login_required
def remove_member(household_id, user_id):
    membership = _get_membership(household_id)
    if not membership:
        return jsonify({'error': 'Not found'}), 404

    if membership.role != 'admin' and user_id != current_user.id:
        return jsonify({'error': 'Forbidden'}), 403

    target = HouseholdMember.query.filter_by(
        user_id=user_id, household_id=household_id, is_active=True
    ).first()
    if not target:
        return jsonify({'error': 'Member not found'}), 404

    target.is_active = False
    target.left_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'success': True})
