import datetime
import concurrent.futures
# Function to get the list of artists the current user follows
def get_followed_artists(sp):
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


# Function to get the albums of an artist released in the last two weeks
def get_recent_albums(sp, artist_id):
    # Get the current date and the date two weeks ago
    today = datetime.datetime.today()
    two_weeks_ago = today - datetime.timedelta(weeks=8)

    # Convert to ISO format for comparison
    two_weeks_ago_str = two_weeks_ago.isoformat()

    # Get albums from the artist
    albums = []
    results = sp.artist_albums(artist_id, album_type='album,single', limit=50)
    albums.extend(results['items'])

    # Check if there are more pages of albums
    while results['next']:
        results = sp.next(results)
        albums.extend(results['items'])

    # Filter albums released in the last two weeks
    recent_albums = [album for album in albums if album['release_date'] >= two_weeks_ago_str]

    return recent_albums

# Function to get albums released in the last two weeks by followed artists
def get_recent_albums_by_followed_artists(sp):
    followed_artists = get_followed_artists(sp)
    all_recent_albums = []

    # Use concurrent.futures to fetch albums for multiple artists in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Map get_recent_albums_for_artist to each artist in the followed_artists list
        results = executor.map(lambda artist: get_recent_albums(sp, artist['id']), followed_artists)

        # Collect all results
        for result in results:
            all_recent_albums.extend(result)

    return all_recent_albums

# Prompt the user to authenticate and get their followed artists
def get_user_followed_artists(sp):
    followed_artists = get_followed_artists(sp)
    print("Artists you follow:")
    for artist in followed_artists:
        print(artist['name'])

# Prompt the user to authenticate and get their recent albums
def get_user_recent_albums(sp):
    recent_albums = get_recent_albums_by_followed_artists(sp)
    print("Recent albums by followed artists (released in the last two weeks):")
    for album in recent_albums:
        album_name = album['name']
        album_url = album['external_urls']['spotify']  # Get the Spotify link for the album
        artist_name = album['artists'][0]['name']
        release_date = album['release_date']

        print(f"Album: {album_name} by {artist_name} (released on {release_date})")
        print(f"Spotify Link: {album_url}")
