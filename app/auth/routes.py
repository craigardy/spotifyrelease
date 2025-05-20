from flask import Blueprint, request, redirect, url_for, session, flash
from app import db
from app.models import User
from app.auth.utils import get_user_spotify_oauth
from sqlalchemy.exc import IntegrityError
from app.backup.utils import link_to_dropbox, upload_sqlite_db
import re
import logging

auth_bp = Blueprint('auth', __name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Verify emails are valid and matching
def isValidEmail(email1, email2):
    if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email1):
        return type(email1) == type(email2) and email1 == email2
    return False

# Route for signing up, initiating Spotify auth process
@auth_bp.route('/signup', methods=['GET'])
def run_script():
    # Validate user email
    user_email1 = request.args.get('email1')
    user_email2 = request.args.get('email2')
    logging.info(f"Signup attempt with email1: {user_email1}, email2: {user_email2}") #Log
    if not isValidEmail(user_email1, user_email2):
        session.clear()
        flash("There was invalid information entered. Please review all information entered and resubmit")
        return redirect(url_for('index'))
    
    session['email'] = user_email1

    sp_oauth = get_user_spotify_oauth()
    # Check if user already exists and has a valid refresh token
    try:
        refresh_token = db.session.query(User.token).filter_by(email=user_email1).scalar()
    except Exception as e:
        logging.error(f"Error querying database for refresh token: {e}")
        flash("A database error occurred. Please try again.")
        return redirect(url_for('index'))
    
    if refresh_token: # if email already in database
        flash("You have already signed up!")
        try:
            token_info = sp_oauth.refresh_access_token(refresh_token)
            if token_info: # If there is a valid token
                sp_oauth.cache_handler.save_token_to_cache(token_info)
                return redirect(url_for('releases.releases'))
        except Exception as e:
            logging.error(f"Error refreshing access token: {e}")
            session.clear()
            flash("Failed to refresh Spotify access token. Please try again.")
            return redirect(url_for('index'))
    # if email not in database (new user) or invalid refresh token, redirect to Spotify auth
    auth_url = sp_oauth.get_authorize_url()
    logging.info(f"Redirecting to Spotify auth URL: {auth_url}") #Log
    return redirect(auth_url)

# Callback route from Spotify auth
@auth_bp.route('/callback')
def callback():
    user_email = session.get('email')
    if not user_email:
        session.clear()
        flash("Email session missing. Please start signup again")
        return redirect(url_for('index'))
    
    code = request.args.get('code')
    logging.info(f"Callback received with code: {code}, user_email: {user_email}") #Log
    sp_oauth = get_user_spotify_oauth()
    try:
        token_info = sp_oauth.get_access_token(code)
    except Exception as e:
        session.clear()
        logging.error(f"Failed to get Spotify access token: {e}")
        flash("Failed to get Spotify access token. Please try again.")
        return redirect(url_for('index'))
    
    # Get refresh token from Spotify response
    refresh_token = token_info.get('refresh_token')
    
    # Update existing user or create new user record
    user = User.query.filter_by(email=user_email).first()
    if user:
        user.token = refresh_token
    else:
        user = User(email=user_email, token=refresh_token)
        db.session.add(user)
    # Commit changes to database
    try:
        db.session.commit()
        logging.info(f"Successfully saved user data to database for email: {user_email}")
        try:
            dbx = link_to_dropbox()
            upload_sqlite_db(dbx, db)
            logging.info("Database uploaded to Dropbox after commit.")
        except Exception as e:
            logging.error(f"Dropbox upload failed after commit: {e}")

        return redirect(url_for('releases.releases'))
    except IntegrityError as e:
        db.session.rollback()
        session.clear()
        logging.error(f"Signup failed due to database error (IntegrityError): {e}")
        flash("Signup failed due to database error. Please try again")
        return redirect(url_for('index'))
    except Exception as e: #Catch other db errors.
        db.session.rollback()
        session.clear()
        logging.error(f"Signup failed due to unexpected database error: {e}")
        flash("Signup failed due to an unexpected database error. Please try again.")
        return redirect(url_for('index'))

    