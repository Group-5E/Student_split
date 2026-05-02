from project.models.base import db
from flask import Blueprint, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from project.models.users import User

households_bp = Blueprint('households',__name__)

@households_bp.route('/me',methods=['GET'])
@login_required
def get_user_households():
    households = [member.household for member in current_user.memberships]
    return jsonify ({'households': [...]})