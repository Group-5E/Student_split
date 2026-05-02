from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from project.models.households import Household, HouseholdMember
from project.models.base import db

households_bp = Blueprint('households',__name__)

@households_bp.route('/create', methods=['POST'])
@login_required
def get_household():
    body = request.get_json()

    household = Household(
        name=body['name'],
        address=body['address'],
        created_by=current_user.id
    )
    db.session.add(household)
    db.session.commit()

    householdMember = HouseholdMember(
        user_id=current_user.id,
        household_id=household.id,
        role="owner"
    )
    db.session.add(householdMember)
    db.session.commit()

    return jsonify({'household': household})


@households_bp.route('/me',methods=['GET'])
@login_required
def get_user_households():
    households = [member.household for member in current_user.memberships]
    return jsonify ({'households': households})
