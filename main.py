import auth
import interface
import notification

def main():
    sp = auth.authenticate()
    email_recipients = ['craig.ardiel@gmail.com']
    email_status = notification.notify_recent_albums(sp, email_recipients)
    if email_status == True:
        interface.save_current_run_time()

if __name__ == "__main__":
    main()
