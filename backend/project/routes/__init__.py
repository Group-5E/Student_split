from .posts import posts_bp
from .auth import auth_bp

def init_app(app):
    app.register_blueprint(posts_bp, url_prefix='/api/posts')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
