from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy instance
db = SQLAlchemy()

def create_app(config_name='development'):
    app = Flask(__name__)

    # Load configuration (Saves Config class attributes in app.config)
    if config_name == 'production':
        app.config.from_object('config.ProductionConfig')
    else:
        app.config.from_object('config.DevelopmentConfig')

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    from app.auth.routes import auth_bp
    from app.releases.routes import releases_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(releases_bp, url_prefix='/releases')

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