import os
from flask import Flask
from config import DevConfig, ProdConfig
from src.extensions import db, login_manager

def create_app():
    app = Flask(__name__)

    # loading
    env_state = os.getenv('FLASK_ENV', 'production')
    if env_state == 'development':
        app.config.from_object(DevConfig)
    else:
        app.config.from_object(ProdConfig)

    # initialization
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    # create db tables
    with app.app_context():
        from src.auth import models
        if not os.path.exists(app.instance_path):
            os.makedirs(app.instance_path)
        db.create_all()

    # blueprints
    from src.auth.routes import auth_bp
    app.register_blueprint(auth_bp)
    from src.main.routes import main_bp
    app.register_blueprint(main_bp)

    return app
