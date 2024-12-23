import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
import interface

load_dotenv()

def send_email(subject, body, to_emails):
    from_email = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASSWORD")

    # Set up the SMTP server
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['Subject'] = subject
    msg['To'] = ', '.join(to_emails)

    msg.attach(MIMEText(body, 'plain'))

    # login to email and send email
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(from_email, password)
        server.sendmail(from_email, to_emails, msg.as_string())
        server.quit()
        print(f"Email sent successfully to {', '.join(to_emails)}")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def format_album_email_body(recent_albums):
    body = "Here are the recent albums released by artists you follow:\n\n"
    for album in recent_albums:
        album_name = album['name']
        album_url = album['external_urls']['spotify']
        artist_name = album['artists'][0]['name']
        release_date = album['release_date']
        body += f"Album: {album_name} by {artist_name}\n"
        body += f"Release Date: {release_date}\n"
        body += f"Spotify Link: {album_url}\n\n"
    return body

def notify_recent_albums(sp, to_emails):
    last_run_time = interface.get_last_run_time()
    recent_albums = interface.get_recent_albums_by_followed_artists(sp, last_run_time)

    if recent_albums:
        email_body = format_album_email_body(recent_albums)
        email_subject = f"Album Releases Since {last_run_time.strftime('%Y-%m-%d')}"
        return send_email(email_subject, email_body, to_emails)
    else:
        print("No new albums released since the last check.")
        return True
