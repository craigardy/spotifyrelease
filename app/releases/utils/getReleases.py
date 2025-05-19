import spotipy
import app.releases.utils.notification as notification

def get_new_releases(access_token, email_recipients, last_ran, session_obj=None):
    if not access_token:
        print("No Spotify access token found. Please authenticate first.")
        return {"email_success": False, "check_success": False}
    try:
        if session_obj:
            sp = spotipy.Spotify(auth=access_token, requests_session=session_obj)
        else:
            sp = spotipy.Spotify(auth=access_token)
    except:
        print("Invalid access token found. Please try authenticating again first.")
        return {"email_success": False, "check_success": False}
    
    return notification.notify_recent_albums(sp, email_recipients, last_ran)
