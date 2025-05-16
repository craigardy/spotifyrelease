from app import create_app, db
from app.models import User
import os

# Create application instance
env = os.getenv('FLASK_ENV', 'development')
app = create_app(env)

# Create database tables
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    if env == 'production':
        from waitress import serve
        serve(app, host="0.0.0.0", port=8000)
    else:
        app.run(host="127.0.0.1", port=5000, debug=True)