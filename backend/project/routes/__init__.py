from .posts import posts_bp

def init_app(app):
    app.register_blueprint(posts_bp, url_prefix='/api/posts')
