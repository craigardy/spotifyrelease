import auth
import interface

def main():
    sp = auth.authenticate()
    #interface.get_user_followed_artists(sp)
    interface.display_recent_albums(sp)

if __name__ == "__main__":
    main()
