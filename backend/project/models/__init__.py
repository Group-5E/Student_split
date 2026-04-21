from .base import db, login_manager

def init_app(app):
    db.init_app(app)
    login_manager.init_app(app)
    with app.app_context():
        db.create_all()
