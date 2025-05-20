from flask import Blueprint, request, jsonify
from app import db
import os
import logging
from app.backup.utils import link_to_dropbox, upload_sqlite_db

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

backup_bp = Blueprint('backup', __name__)

@backup_bp.route('/run-backup', methods=['POST'])
def generate_db_backup():
    # Get the secret key from environment
    secret_key = os.environ.get('CRON_SECRET_KEY_BACKUP')
    
    # Verify secret token from request headers
    auth_token = request.headers.get('X-API-Key')
    if not auth_token or auth_token != secret_key:
        logger.warning("Unauthorized attempt to access scheduled task endpoint")
        return jsonify({"error": "Unauthorized"}), 401
    
    logger.info("Authorized request received for scheduled releases task")

    try:
        dbx = link_to_dropbox()
    except Exception as e:
        logger.error(f"Failed to link to Dropbox: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to link to Dropbox: {str(e)}"
        }), 500
    
    try:
        upload_sqlite_db(dbx, db)
        logger.info("Database successfully uploaded to Dropbox.")
        return jsonify({"status": "success", "message": "Backup completed successfully."}), 200
    except Exception as e:
        logger.error(f"Failed to upload database to Dropbox: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Backup failed: {str(e)}"
        }), 500


    