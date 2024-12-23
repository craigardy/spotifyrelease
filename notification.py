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

    msg.attach(MIMEText(body, 'html'))

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
    html_body = """
    <html>
    <body style="text-align: center; font-family: Arial, sans-serif;">
    """
    for album in recent_albums:
        album_name = album['name']
        album_url = album['external_urls']['spotify']
        artist_name = album['artists'][0]['name']
        release_date = album['release_date']
        cover_art_url = album['images'][0]['url'] if album['images'] else None

        html_body += f"""
        <div style="margin-bottom: 30px;">
            <p style="margin: 0; line-height: 1.2;"><strong>{album_name}</strong> by {artist_name}</p>
            <p style="margin: 0; line-height: 1.2;">Release Date: {release_date}</p>
            {"<a href='" + album_url + "'><img src='" + cover_art_url + "' alt='" + album_name + "' style='width: 300px; height: 300px; margin-top: 5px;'></a>" if cover_art_url else ""}
        </div>
        """

    html_body += "</body></html>"
    return html_body

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
