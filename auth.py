import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

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

# Function to get the list of artists the current user follows
def get_followed_artists():
    # The list of followed artists
    followed_artists = []

    # Initial request to get followed artists (50 per request, Spotify API limit)
    results = sp.current_user_followed_artists(limit=50)
    followed_artists.extend(results['artists']['items'])

    # Check if there are more pages of artists
    while results['artists']['next']:
        results = sp.next(results['artists'])
        followed_artists.extend(results['artists']['items'])

    return followed_artists

# Function to display artist names
def display_followed_artists():
    followed_artists = get_followed_artists()
    print("Artists you follow:")
    for artist in followed_artists:
        print(artist['name'])

# Prompt the user to authenticate and get their followed artists
def get_user_followed_artists():
    print("Please log in to your Spotify account to view followed artists.")
    # Authenticate the user and retrieve their followed artists
    display_followed_artists()

if __name__ == "__main__":
    get_user_followed_artists()
