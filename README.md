# Spotify Release Notifications

Spotify stopped sending regular emails on new releases from artists you follow. For the fellow music lovers, you can use this app to stay up to date with new music from your favourite artists on Spotify. This application sends you regular email updates about the latest releases from the artists you follow on Spotify.

**[Live Demo](https://spotifyrelease.onrender.com)**

## How It Works

1. Sign up with your email address
2. Authorize access to your Spotify followed artists
3. Receive an initial email with all new releases from the past 4 weeks
4. Get bi-weekly updates with all new music

## Tech Stack

- **Backend**: Python, Flask, Flask Blueprints, SQLAlchemy
- **Database**: SQLite
- **APIs**: Spotify Web API (via Spotipy), Dropbox API
- **Frontend**: HTML, CSS, JavaScript
- **Deployment**: Render, Waitress

## Implementation Details

This project was built using Flask for the backend, handling routing, user sessions, and integrating with the Spotify API. Flask Blueprints were used to organize application routes for better code modularity. SQLAlchemy was employed as an ORM to interact with the SQLite database, defining data models and performing operations. Email notifications are automated using Python's email.mime library within the Flask application. User authentication and navigation are implemented using Flask's redirect, url_for, and session features.

For API interaction, the Spotipy library was utilized to interact with the Spotify Web API, retrieving artist and release information. concurrent.futures.ThreadPoolExecutor was used to efficiently fetch data from the Spotify API by making concurrent requests. The Dropbox API is also used for database backups.

On the frontend, JavaScript implements client-side email validation. Regular Expressions (re) are employed for robust validation of user-provided email addresses.

The application uses SQLite for local data storage. Configuration management is handled with Flask Configuration Classes for different application environments (development, production), and python-dotenv is used to manage environment variables for sensitive information like API keys.

For production deployments, the application is served using waitress. Version control is managed with Git, and the source code is available on GitHub.

## Optimizations

The primary goal for this project was to run the application at little to no cost. I successfully achieved this by leveraging free-tier services and implementing creative workarounds for common limitations. Here's how:

**Hosting:**
The app is hosted on **[Render](https://render.com/)**, which offers a free tier for web services. A key limitation of this tier is that the service spins down after 15 minutes of inactivity. When this happens, the first user to revisit the site may experience a delay of up to a minute while the service restarts. To mitigate this, I use a cron job that periodically pings the site, keeping the site available. I used **[cron-job.org](https://cron-job.org/en/)**, which is free to use.

**Scheduled Jobs:**
Email updates are sent to users every two weeks. This is handled by a cron job that sends a POST request to the /scheduled/run-releases endpoint of the website. The request includes a secret key for authentication. When authorized, the server retrieves all users from the database, fetches the recent relases from the Spotify API using Spotipy the framework, and sends personalized emails to each user.

**Database Persistence:**
Render's free database offering is temporary and gets deleted after 30 days. Since the app only needs to store basic user data (like email addresses), I opted to manage the database directly at the OS level. After every update, the database is encoded and uploaded to Dropbox using the Dropbox API. When the server restarts, the latest backup from Dropbox is downloaded, decoded, and restored - ensuring persistent data across deployments. Given the small scale of the application, the solution is both simple and effective.

## Lessons Learned

Building this application offered hands-on experience with several important concepts in web development and deployment:

- **API Interaction and Rate Limiting:** 
Implementing robust error handling and exponential backoff strategies for the Spotify API, especially for refreshing access tokens and handling rate limits, was a significant learning curve. It highlighted the importance of designing systems that can gracefully handle external service constraints.

- **Data Persistence in Resource-Constrained Environments:** 
Operating within the limitations of free hosting highlighted the challenges of maintaining persistent data without a permanent database. Using Dropbox as a backup solution pushed me to think creatively about data durability, backup strategies, and recovery processes.

- **Scheduled Tasks and Automation:** 
Implementing cron jobs for both keeping the server active and triggering biweekly email notifications gave me practical insight into task scheduling in web applications. It showed me how automation can be a powerful tool for reliability and user engagement.

- **Modularity with Flask Blueprints:** 
Structuring the app using Flask Blueprints helped improve the organization, scalability, and maintainability of the codebase—especially important as the project grew in complexity.
 
- **Client-side Validation:** 
Integrating JavaScript with regular expressions for email validation emphasized the importance of validating user input early. It also highlighted how frontend improvements can enhance both usability and data quality.

## Self-Hosting Guide

Want to run your own instance? Follow these steps:

### Prerequisites
- GitHub account
- Render account
- Dropbox developer account
- Spotify developer account
- Gmail account (recommended for notifications)

### Setup Instructions

1. **Fork the Repository**
   - Fork this GitHub repo to your account

2. **Create a Render Web Service**
   - Point to your forked repository
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn wsgi:app`
   - Note your service URL for later use

3. **Set Up Dropbox API**
   - Create a developer account at https://www.dropbox.com/developers/
   - Create a new app with App folder access named "spotifyrelease-db-backup"
   - Under Permissions, enable files.content.write and files.content.read
   - Note your App Key and App Secret
   - Create a "backups" folder in your Apps/spotifyrelease-db-backups directory

4. **Generate Dropbox Refresh Token**
   Run this Python script once to get your refresh token, and note the refresh token for later use. Remember to first replace your App key and secret before running the script!
   ```python
   import dropbox
   import urllib.parse

   # Replace with your actual App Key and App Secret
   APP_KEY = "YOUR_APP_KEY"
   APP_SECRET = "YOUR_APP_SECRET"

   # Create a Dropbox OAuth2Flow object
   auth_flow = dropbox.DropboxOAuth2FlowNoRedirect(APP_KEY, APP_SECRET)

   # Construct the authorization URL with token_access_type='offline'
   authorize_base_url = "https://www.dropbox.com/oauth2/authorize"
   params = {
       'client_id': APP_KEY,
       'response_type': 'code',
       'token_access_type': 'offline', 
   }
   authorize_url = f"{authorize_base_url}?{urllib.parse.urlencode(params)}"

   print("1. Go to this URL and log in to your Dropbox account:")
   print(authorize_url)
   print("2. Click 'Allow' to grant permission to your app.")

   # Get the authorization code from user
   auth_code = input("3. Copy the authorization code and paste it here: ").strip()

   # Exchange authorization code for access token and refresh token
   try:
       oauth_result = auth_flow.finish(auth_code)
       print("\n--- OAuth Result ---")
       print(f"Refresh Token: {oauth_result.refresh_token}")
       print("\nStore the Refresh Token securely.")
   except Exception as e:
       print(f"An error occurred: {e}")
   ```

5. **Set Up Spotify API**
   - Create a developer account at https://developer.spotify.com/
   - Create a new app from the Dashboard
   - Add a Redirect URI: `https://YOUR-RENDER-URL.onrender.com/auth/callback`
   - Note your Client ID and Client Secret

6. **Generate Secret Keys**
   - Create three different 32-byte secret keys using Python's `secrets` module:
     - One for cron job authentication
     - One for database encryption
     - One for Flask sessions

7. **Set Up Gmail App Password** (if using Gmail)
   - Follow Section 2 instructions at https://github.com/craigardy/mySparkleNotification

8. **Configure Environment Variables**
   - In your Render web service, add these environment variables, replacing the values below with the values created from the previous steps:
   ```
   CRON_SECRET_KEY=Your_Cron_Job_Secret_Key
   DB_ENCRYPTION_KEY=Your_DB_Encryption_Key
   DROPBOX_ACCESS_TOKEN=Your_Dropbox_ACCESS_TOKEN
   EMAIL_PASSWORD=Your_Gmail_APP_Password
   EMAIL_USER=your_email@gmail.com
   FLASK_SECRET_KEY=Your_Flask_Secret_Key
   SPOTIPY_CLIENT_ID=Your_Spotify_Client_ID
   SPOTIPY_CLIENT_SECRET=Your_Spotify_Secret
   SPOTIPY_REDIRECT_URI=https://YOUR-RENDER-URL.onrender.com/auth/callback
   DROPBOX_APP_KEY=Your_Dropbox_App_Key
   DROPBOX_APP_SECRET=Your_Dropbox_App_Secret
   DROPBOX_REFRESH_TOKEN=Your_Dropbox_Refresh_Token
   ```

9. **Set Up Cron Jobs**
   - Create an account at https://cron-job.org/en/
   - Create two cron jobs:
     - Job 1: GET request to your homepage every 10 minutes
     - Job 2: POST request to `/scheduled/run-releases` on the 1st and 15th of each month
       - Add header `X-API-KEY` with value matching your `CRON_SECRET_KEY`

10. **Create Initial Database**
    - Create a `site.db` file with this schema:
    ```sql
    CREATE TABLE users (
        email    TEXT PRIMARY KEY,
        token    TEXT NOT NULL,
        last_ran TEXT
    );
    ```
    - Place it in the `instance` folder of your repository
    - Manually deploy your latest commit on Render
    - Visit your site and sign up with your email to initialize the database (This is to initialize dropbox site.db.enc)
    - Remove the `site.db` file from your repository after initialization
    - Manually deploy your latest commit on Render

Your Spotify Release Notifications app should now be up and running!
