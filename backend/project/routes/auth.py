from project.models.base import db
from werkzeug.security import generate_password_hash, check_password_hash
from project.models.users import User
from flask import Blueprint, request, jsonify
from flask_login import login_user, login_required, logout_user, current_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=["POST"])
def register():
    body = request.get_json()
    existing = User.query.filter_by(email=body['email']).first()
    print(f"user for {body['email']}: {existing}")
    if existing:
        return jsonify({ 'error': 'Email already in use' }), 400
    user = User(
        username=body['username'],
        name=body['name'],
        email=body['email'],
        password_hash=generate_password_hash(body['password'])
    )
    db.session.add(user)
    db.session.commit()
    login_user(user)
    return jsonify({ 'success': True })

@auth_bp.route('/login', methods=['POST'])
def login():
    body = request.get_json()
    user = User.query.filter_by(email=body['email']).first()
    if not (user):
        return jsonify({ 'error': 'user not found' }), 401
    elif not check_password_hash(user.password_hash, body['password']):
        return jsonify({ 'error': 'Invalid credentials' }), 401
    login_user(user)
    return jsonify({ 'success': True })


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({ 'success': True })

@auth_bp.route('/me', methods=['GET'])
def me():
    if not current_user.is_authenticated:
        return jsonify({ 'user': None })
    return jsonify({ 'user': {
        'id': current_user.id,
        'email': current_user.email,
        'username': current_user.username,
    } })


# @auth_bp.route('/github')
# def github_login():
#     redirect_uri = url_for('auth.github_callback', _external=True)
#     return github.authorize_redirect(redirect_uri)
#
# @auth_bp.route('/github/callback')
# def github_callback():
#     token = github.authorize_access_token()
#     resp = github.get('user', token=token)
#     profile = resp.json()
#     user = User.query.filter_by(github_id=str(profile['id'])).first()
#     if not user:
#         user = User(github_id=str(profile['id']), name=profile['name'])
#         db.session.add(user)
#         db.session.commit()
#     login_user(user)
#     return redirect('http://localhost:5173')  # redirect back to Vite
