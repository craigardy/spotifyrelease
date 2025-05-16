import os
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

class Config:
    # Initialize Flask app and set configurations
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", os.urandom(24)) # Set secret key for session
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db' # SQLite database
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Load Spotify credentials and permissions scope
    CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
    CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
    REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")
    SCOPE = "user-follow-read user-library-read"

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False