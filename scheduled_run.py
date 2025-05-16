from app.releases.utils.getReleases import get_new_releases
from app import create_app, db
from app.models import User
import datetime
import requests
from config import Config
import time

# Custom session with increased connection pool
spotify_session = requests.Session()
adapter = requests.adapters.HTTPAdapter(pool_connections=50, pool_maxsize=50, pool_block=True)
spotify_session.mount('https://', adapter)

import time

def refresh_access_token(refresh_token):
    while True:
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
            retry_after = int(response.headers.get("Retry-After", 5))
            print(f"Rate limited. Retrying after {retry_after} seconds.")
            time.sleep(retry_after)
            continue
        if response.status_code != 200:
            raise Exception(f"Token refresh failed: {response.text}")
        return response.json()['access_token']


def run_for_all_users():
    all_users = User.query.all()
    for user in all_users:
        try:
            access_token = refresh_access_token(user.token)
            if not user.last_ran:
                last_ran_time = datetime.datetime.today() - datetime.timedelta(weeks=4)
            else:
                last_ran_time = datetime.datetime.fromisoformat(user.last_ran)
            email_status = get_new_releases(access_token, [user.email], last_ran_time)
            if (email_status.get("email_success") == True or email_status.get("check_success") == True):
                user.last_ran = datetime.datetime.today().isoformat()
        except Exception as e:
            print(f"Failed for {user.email}: {e}")
        time.sleep(0.2)
    try:
        db.session.commit()
    except:
        print(f"Failed to update last_ran date for {user.email}")

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        run_for_all_users()