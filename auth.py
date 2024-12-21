import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

def authenticate():
    # Load environment variables from .env file
    load_dotenv()

    # Fetch credentials from environment variables
    CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
    CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
    REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")

    # Ensure these environment variables are set
    if not CLIENT_ID or not CLIENT_SECRET or not REDIRECT_URI:
        print("Please set the SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, and SPOTIPY_REDIRECT_URI environment variables.")
        exit(1)

    # Set the scope to access the user's followed artists
    SCOPE = "user-follow-read"

    # Authenticate with Spotify using OAuth
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                                client_secret=CLIENT_SECRET,
                                                redirect_uri=REDIRECT_URI,
                                                scope=SCOPE))
    return sp

if __name__ == "__main__":
    sp = authenticate()
