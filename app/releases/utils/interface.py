import datetime
import concurrent.futures

# Function to get the list of artists the current user follows
def get_followed_artists(sp):
    followed_artists = []
    results = sp.current_user_followed_artists(limit=50)
    followed_artists.extend(results['artists']['items'])

    # Check if there are more pages of artists
    while results['artists']['next']:
        results = sp.next(results['artists'])
        followed_artists.extend(results['artists']['items'])
    return followed_artists


# Function to get the albums of an artist released in the last two weeks
def get_recent_albums(sp, artist_id, last_run_time):
    albums = []
    results = sp.artist_albums(artist_id, album_type='album,single', limit=50)
    albums.extend(results['items'])

    recent_albums = []
    for album in albums:
        # Handle the case where the release date is just a year (e.g., '2018'), make it the first day of the year
        try:
            release_date_str = album['release_date']
            if len(release_date_str) == 4:
                release_date_str += "-01-01"
            release_date = datetime.datetime.fromisoformat(release_date_str)
        except ValueError:
            # If the date is invalid or cannot be parsed, skip the album
            continue
        # Only add albums released after the last run time
        if release_date > last_run_time:
            recent_albums.append(album)
    return recent_albums

# Function to get albums released in the last two weeks by followed artists
def get_recent_albums_by_followed_artists(sp, last_run_time):
    followed_artists = get_followed_artists(sp)
    all_recent_albums = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(lambda artist: get_recent_albums(sp, artist['id'], last_run_time), followed_artists)
        for result in results:
            all_recent_albums.extend(result)
    return all_recent_albums
