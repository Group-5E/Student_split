from flask_cors import CORS
import os
from flask import Flask

def create_app(config=None):
    from . import models, routes
    app = Flask(__name__)

    # load default configuration
    app.config.from_object('project.settings')

    # load environment configuration
    if 'FLASK_CONF' in os.environ:
        app.config.from_envvar('FLASK_CONF')

    # load app specific configuration
    if config is not None:
        if isinstance(config, dict):
            app.config.update(config)
        elif config.endswith('.py'):
            app.config.from_pyfile(config)

    models.init_app(app)
    routes.init_app(app)

    CORS(app, supports_credentials=True, origins=['http://localhost:5173'])

    return app
