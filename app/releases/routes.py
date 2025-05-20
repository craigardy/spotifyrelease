from flask import Blueprint, redirect, url_for, session, flash
from app import db
from app.models import User
from app.auth.utils import get_user_spotify_oauth, get_valid_token
from app.releases.utils.getReleases import get_new_releases
from app.backup.utils import link_to_dropbox, upload_sqlite_db
import datetime
from sqlalchemy.exc import IntegrityError
import logging

releases_bp = Blueprint('releases', __name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Route to get new releases from followed artists
@releases_bp.route('/get-releases')
def releases():
    user_email = session.get('email')
    if not user_email:
        session.clear()
        flash("Email session missing. Please start signup again")
        return redirect(url_for('index'))
    
    sp_oauth = get_user_spotify_oauth()
    token_info = get_valid_token(sp_oauth)
    if not token_info:
        session.clear()
        flash("Signup failed due to access token error. Please try again")
        return redirect(url_for('index'))
    
    access_token = token_info['access_token']
    # get the last time the user ran from database, otherwise defaults to 4 weeks.
    last_ran_str = db.session.query(User.last_ran).filter_by(email=user_email).scalar()
    
    if not last_ran_str:
        last_ran_time = datetime.datetime.today() - datetime.timedelta(weeks=4)
    else:
        last_ran_time = datetime.datetime.fromisoformat(last_ran_str)

    logging.info(f"User email: {user_email}, Last ran: {last_ran_time}")
    
    try:
        session_obj = sp_oauth.session_obj
        success = get_new_releases(access_token, [user_email], last_ran_time, session_obj=session_obj)
        logging.info(f"get_new_releases result: {success}")
    except Exception as e:
        logging.error(f"Error in get_new_releases: {e}")
        flash(f"Error getting new releases: {e}")
        return redirect(url_for('index'))
    
    if not success["email_success"] and not success["check_success"]:
        flash("Unable to pull artists new releases. Please try again.")
    else:
        # if successful, update user's last_ran time in database with todays date
        now = datetime.datetime.today()
        now_str = now.isoformat()

        # Update existing user or create new user record
        user = User.query.filter_by(email=user_email).first()
        if user:
            user.last_ran = now_str
        else:
            logging.warning(f"User with email {user_email} not found in database.")

        # Commit changes to database
        try:
            db.session.commit()
            try:
                dbx = link_to_dropbox()
                upload_sqlite_db(dbx, db)
                logging.info("Database uploaded to Dropbox after commit.")
            except Exception as e:
                logging.error(f"Dropbox upload failed after commit: {e}")
        except IntegrityError:
            db.session.rollback()
            session.clear()
            logging.error(f"Database error: {e}")
            flash("Unable to get recently released music due to database error. Please try again")
            return redirect(url_for('index'))
        except Exception as e: #Catch other potential db errors
            db.session.rollback()
            session.clear()
            logging.error(f"Unexpected database error: {e}")
            flash("An unexpected database error occurred. Please try again.")
            return redirect(url_for('index'))
        
        if not success["email_success"] and success["check_success"]:
            session.clear()
            flash(f"No new releases since last checked: {last_ran_time}")
        else:
            session.clear()
            flash(f"success! Email sent to {user_email}")
    return redirect(url_for('index'))
