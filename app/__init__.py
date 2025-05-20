from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from app.backup.utils import link_to_dropbox, download_sqlite_db
import os
import logging

# Initialize SQLAlchemy instance
db = SQLAlchemy()

def create_app(config_name='development'):
    app = Flask(__name__)

    # Load configuration (Saves Config class attributes in app.config)
    if config_name == 'production':
        app.config.from_object('config.ProductionConfig')
    else:
        app.config.from_object('config.DevelopmentConfig')

    # Ensure intance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    # Load DB from Dropbox before initializing extensions
    local_db_path = os.path.join(app.instance_path, 'site.db')
    with app.app_context():
        if not os.path.exists(local_db_path):
            try:
                logging.info(f"site.db not found locally, downloading from Dropbox...")
                dbx = link_to_dropbox()
                download_sqlite_db(dbx)
            except Exception as e:
                logging.error(f"Failed to download database from Dropbox: {e}")


    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    from app.auth.routes import auth_bp
    from app.releases.routes import releases_bp
    from app.scheduled.routes import scheduled_bp
    from app.backup.routes import backup_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(releases_bp, url_prefix='/releases')
    app.register_blueprint(scheduled_bp, url_prefix='/scheduled')
    app.register_blueprint(backup_bp, url_prefix='/backup')

    # Register main routes
    @app.route('/')
    @app.route('/index')
    def index():
        from flask import render_template
        # Preserve flashed messages
        flashes = session.get('_flashes', None)
        session.clear()
        if flashes:
            session['_flashes'] = flashes
        return render_template('index.html')

    return app