from .base import db, login_manager
from . import households, users, payment, expenses
from .views import create_views

def init_app(app):
    db.init_app(app)
    login_manager.init_app(app)
    with app.app_context():
        db.create_all()
        create_views(db.engine)
