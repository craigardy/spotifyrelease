import datetime
import concurrent.futures
import os

# Function to get the last run time from a text file
# Default is 2 weeks ago if program not ran yet.
def get_last_run_time():
    # Path to the text file that stores the last run time
    last_run_file = 'last_run.txt'

    # If the file doesn't exist, return a default of two weeks ago
    if not os.path.exists(last_run_file):
        two_weeks_ago = datetime.datetime.today() - datetime.timedelta(weeks=2)
        return two_weeks_ago

    # Read the last run time from the file
    try:
        with open(last_run_file, 'r') as file:
            last_run_str = file.read().strip()
            # If the file is empty or the date is not valid, return a default value
            if not last_run_str:
                raise ValueError("File is empty.")
            return datetime.datetime.fromisoformat(last_run_str)
    except (ValueError, OSError) as e:
        # If there's an error reading or parsing the date, return a default value
        print(f"Error reading last run time: {e}. Defaulting to two weeks ago.")
        two_weeks_ago = datetime.datetime.today() - datetime.timedelta(weeks=2)
        return two_weeks_ago

# Function to save the current run time to a text file
def save_current_run_time():
    now = datetime.datetime.today()
    with open('last_run.txt', 'w') as file:
        file.write(now.isoformat())

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

# Display the recent albums released after the last run time
def display_recent_albums(sp):
    last_run_time = get_last_run_time()
    # Format the last run time to 'YYYY-MM-DD'
    last_run_time_str = last_run_time.strftime('%Y-%m-%d')

    recent_albums = get_recent_albums_by_followed_artists(sp, last_run_time)

    print(f"Recent albums by followed artists (released since {last_run_time_str}):")
    for album in recent_albums:
        album_name = album['name']
        album_url = album['external_urls']['spotify']
        artist_name = album['artists'][0]['name']
        release_date = album['release_date']

        print(f"Album: {album_name} by {artist_name} (released on {release_date})")
        print(f"Spotify Link: {album_url}")

    # Save the current run time for the next execution
    save_current_run_time()
