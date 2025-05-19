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
    app.run(host="127.0.0.1", port=5000, debug=True)