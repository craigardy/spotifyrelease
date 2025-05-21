from flask import current_app
import dropbox
from config import Config
from sqlalchemy.exc import SQLAlchemyError
import logging
import os
from cryptography.fernet import Fernet

# Configure logging (if not already configured globally)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

ENCRYPTION_KEY = os.getenv('DB_ENCRYPTION_KEY')

def encrypt_file(input_path, output_path):
    fernet = Fernet(ENCRYPTION_KEY.encode())
    with open(input_path, 'rb') as f:
        data = f.read()
    encrypted = fernet.encrypt(data)
    with open(output_path, 'wb') as f:
        f.write(encrypted)

def decrypt_file(input_path, output_path):
    fernet = Fernet(ENCRYPTION_KEY.encode())
    with open(input_path, 'rb') as f:
        encrypted_data = f.read()
    decrypted = fernet.decrypt(encrypted_data)
    with open(output_path, 'wb') as f:
        f.write(decrypted)


def link_to_dropbox():
    if not Config.DROPBOX_APP_KEY or not Config.DROPBOX_APP_SECRET or not Config.DROPBOX_REFRESH_TOKEN:
        logger.error("Dropbox API credentials (APP_KEY, APP_SECRET, or REFRESH_TOKEN) are missing.")
        raise ValueError("Dropbox API credentials are not fully configured.")
    
    try:
        dbx = dropbox.Dropbox(
            app_key=Config.DROPBOX_APP_KEY,
            app_secret=Config.DROPBOX_APP_SECRET,
            oauth2_refresh_token=Config.DROPBOX_REFRESH_TOKEN
        )
        # Verify connection
        dbx.users_get_current_account()
        logger.info("Successfully linked to Dropbox using refresh token.")
        return dbx
    except dropbox.exceptions.AuthError as e:
        logger.error(f"Dropbox authentication error: {e}. Please check your refresh token and app credentials.")
        raise
    except Exception as e:
        logger.error(f"Failed to link to Dropbox: {e}")
        raise


def download_sqlite_db(dbx, dropbox_path='/backups/site.db.enc'):
    db_path = os.path.join(current_app.instance_path, 'site.db')

    encrypted_db_path = db_path + '.enc'

    try:
        logger.info(f"Downloading database from Dropbox to {db_path}...")
        metadata, res = dbx.files_download(dropbox_path)
        os.makedirs(os.path.dirname(encrypted_db_path), exist_ok=True)
        with open(encrypted_db_path, 'wb') as f:
            f.write(res.content)
        logger.info("Database successfully downloaded from Dropbox.")
        decrypt_file(encrypted_db_path, db_path)
        os.remove(encrypted_db_path)
    except dropbox.exceptions.ApiError as e:
        logger.warning(f"Could not download database from Dropbox: {e}")
    except Exception as e:
        logger.error(f"Unexpected error while downloading DB from Dropbox: {e}")

def upload_sqlite_db(dbx, db_instance):
    db_path = os.path.join(current_app.instance_path, 'site.db')
    logger.info(f"Resolved database path: {db_path}")
    # Attempt to commit database changes
    try:
        db_instance.session.commit()
        logger.info("Database commit successful.")
    except SQLAlchemyError as e:
        db_instance.session.rollback()
        logger.error(f"Database commit failed: {e}")
        raise RuntimeError(f"Database commit failed: {e}")

    encrypted_path = db_path + '.enc'
    encrypt_file(db_path, encrypted_path)
    dropbox_dest_path = '/backups/site.db.enc'

    # Proceed to upload to dropbox only if commit succeeded
    try:
        with open(encrypted_path, 'rb') as f:
            dbx.files_upload(f.read(), dropbox_dest_path, mode=dropbox.files.WriteMode.overwrite)
            logger.info(f"Successfully uploaded {db_path} to Dropbox.")
    except Exception as e:
        logger.error(f"Dropbox upload failed: {e}")
        raise RuntimeError(f"Dropbox upload failed: {e}")