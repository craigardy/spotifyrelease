from app.releases.utils.getReleases import get_new_releases
from app import db
from app.models import User
import datetime
import requests
from config import Config
import time
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Custom session with increased connection pool
spotify_session = requests.Session()
adapter = requests.adapters.HTTPAdapter(pool_connections=50, pool_maxsize=50, pool_block=True)
spotify_session.mount('https://', adapter)

# Rate limiting constants
BASE_DELAY = 1.0  # Base delay between API requests in seconds
MAX_RETRIES = 5   # Maximum number of retries for a failed request
MAX_BACKOFF = 60  # Maximum backoff time in seconds

def refresh_access_token(refresh_token, retry_count=0):
    """Refresh the Spotify access token with exponential backoff for rate limits"""
    try:
        response = spotify_session.post(
            'https://accounts.spotify.com/api/token',
            data={
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token,
                'client_id': Config.CLIENT_ID,
                'client_secret': Config.CLIENT_SECRET
            },
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        if response.status_code == 429:
            # Get retry time from header or use exponential backoff
            retry_after = int(response.headers.get("Retry-After", min(2 ** retry_count, MAX_BACKOFF)))
            logger.warning(f"Rate limited when refreshing token. Retrying after {retry_after} seconds.")
            time.sleep(retry_after)
            # Recursive call with increased retry count
            return refresh_access_token(refresh_token, retry_count + 1)
            
        if response.status_code != 200:
            logger.error(f"Token refresh failed: {response.text}")
            raise Exception(f"Token refresh failed: {response.text}")
            
        return response.json()['access_token']
    except requests.exceptions.RequestException as e:
        if retry_count < MAX_RETRIES:
            # Network error, retry with backoff
            backoff_time = min(2 ** retry_count, MAX_BACKOFF)
            logger.warning(f"Network error during token refresh. Retrying after {backoff_time} seconds.")
            time.sleep(backoff_time)
            return refresh_access_token(refresh_token, retry_count + 1)
        else:
            logger.error(f"Max retries exceeded for token refresh: {e}")
            raise

def rate_limited_get_new_releases(access_token, email, last_ran, retry_count=0):
    """Wrapper for get_new_releases with rate limiting and exponential backoff"""
    try:
        # Add base delay between API request sets
        time.sleep(BASE_DELAY)
        
        # Call the actual function
        return get_new_releases(access_token, [email], last_ran, spotify_session)
    except Exception as e:
        # Check if it's a rate limit error
        if "429" in str(e) and retry_count < MAX_RETRIES:
            # Extract retry time if available, otherwise use exponential backoff
            retry_time = None
            if hasattr(e, 'headers') and 'Retry-After' in e.headers:
                retry_time = int(e.headers['Retry-After'])
            else:
                retry_time = min(2 ** retry_count, MAX_BACKOFF)
            
            logger.warning(f"Rate limited for {email}. Backing off for {retry_time} seconds.")
            time.sleep(retry_time)
            
            # Retry with increased count
            return rate_limited_get_new_releases(access_token, email, last_ran, retry_count + 1)
        else:
            # Not a rate limit error or max retries exceeded
            raise


def run_scheduled_releases():
    results = {
        "total_users": 0,
        "successful_users": 0,
        "failed_users": 0
    }

    all_users = User.query.all()
    results["total_users"] = len(all_users)

    logger.info(f"Starting scheduled run for {len(all_users)} users")
    
    for user in all_users:
        try:
            logger.info(f"Processing user: {user.email}")
            access_token = refresh_access_token(user.token)
            
            if not user.last_ran:
                last_ran_time = datetime.datetime.today() - datetime.timedelta(weeks=4)
            else:
                last_ran_time = datetime.datetime.fromisoformat(user.last_ran)
                
            # Use rate-limited wrapper function
            email_status = rate_limited_get_new_releases(access_token, user.email, last_ran_time)
            
            if (email_status.get("email_success") == True or email_status.get("check_success") == True):
                user.last_ran = datetime.datetime.today().isoformat()
                logger.info(f"Successfully updated for {user.email}")
                results["successful_users"] += 1
                
            # Add a delay between processing different users
            time.sleep(2)  # Increased from 0.2 to 2 seconds
            
        except Exception as e:
            logger.error(f"Failed for {user.email}: {str(e)}")
            results["failed_users"] += 1
    
    try:
        db.session.commit()
        logger.info("Successfully committed all user updates")
        return results
    except Exception as e:
        logger.error(f"Failed to update database: {str(e)}")
        db.session.rollback()
        raise