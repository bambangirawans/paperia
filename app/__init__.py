import logging
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        db.create_all()

    from .routes import main_bp
    app.register_blueprint(main_bp)

    # Configure logging inside the application context
    #logging.basicConfig(filename='error.log', level=logging.ERROR)
    logging.basicConfig(filename='app.log', level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s')

    return app
