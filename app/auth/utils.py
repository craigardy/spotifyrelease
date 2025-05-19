import requests
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import CacheHandler
from flask import session
from config import Config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Custom CacheHandler to store Spotify tokens in Flask session
class SessionCacheHandler(CacheHandler):
    def __init__(self, session_key='token_info'):
        self.session_key = session_key

    # Spotipy calls to read token in session['token_info']
    def get_cached_token(self):
        return session.get(self.session_key)

    # Spotipy calls to store token in session['token_info']
    # saved to session when running sp_oauth.get_access_token(code)
    def save_token_to_cache(self, token_info):
        session[self.session_key] = token_info


# Helper to create a SpotifyOAuth instance with session caching and custom HTTP settings
def get_user_spotify_oauth():
    session_obj = requests.Session()
    adapter = requests.adapters.HTTPAdapter(pool_connections=50, pool_maxsize=50, pool_block=True)
    session_obj.mount('https://', adapter)

    # Log the session object and its adapter configuration
    https_adapter = session_obj.adapters.get('https://')
    if https_adapter:
        logging.info(f"Adapter for 'https://': {https_adapter}")

        # Access PoolManager (only available if urllib3 is used)
        poolmanager = getattr(https_adapter, 'poolmanager', None)
        if poolmanager:
            logging.info(f"PoolManager connections: {poolmanager.connection_pool_kw.get('maxsize')}")
            logging.info(f"PoolManager config: {poolmanager.connection_pool_kw}")
        else:
            logging.warning("PoolManager not found on HTTPS adapter.")
    else:
        logging.warning("No 'https://' adapter found in the session.")


    # Create the SpotifyOAuth instance with the custom session
    sp_oauth = SpotifyOAuth(
        client_id=Config.CLIENT_ID,
        client_secret=Config.CLIENT_SECRET,
        redirect_uri=Config.REDIRECT_URI,
        scope=Config.SCOPE,
        cache_handler=SessionCacheHandler(),
        requests_session=session_obj  # Attach the custom session here
    )

    sp_oauth.session_obj = session_obj

    return sp_oauth

# Helper function to ensure token is valid and refresh if expired
def get_valid_token(sp_oauth):
    """
    Grabs the token information from the sp_oauth session. If there is a current token in the session cache, then check if the access token is expired. If access token is expired, then get a new access token and update so_oauth session with new access token.
    """
    token_info = sp_oauth.get_cached_token()
    if not token_info:
        return None
    
    if sp_oauth.is_token_expired(token_info):
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        sp_oauth.cache_handler.save_token_to_cache(token_info)
    return token_info