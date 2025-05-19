from app import create_app, db
import os

# Create production application instance
env = os.getenv('FLASK_ENV', 'production')  # Default to production
app = create_app(env)

# The 'app' object is what Gunicorn will use
if __name__ == "__main__":
    # Create database tables if needed
    with app.app_context():
        db.create_all()