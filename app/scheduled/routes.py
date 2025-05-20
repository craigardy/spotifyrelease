from flask import Blueprint, request, jsonify
import os
import logging
from app.scheduled.utils import run_scheduled_releases

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

scheduled_bp = Blueprint('scheduled', __name__)

@scheduled_bp.route('/run-releases', methods=['POST'])
def run_scheduled_task():
    # Get the secret key from environment
    secret_key = os.environ.get('CRON_SECRET_KEY')
    
    # Verify secret token from request headers
    auth_token = request.headers.get('X-API-Key')
    if not auth_token or auth_token != secret_key:
        logger.warning("Unauthorized attempt to access scheduled task endpoint")
        return jsonify({"error": "Unauthorized"}), 401
    
    logger.info("Authorized request received for scheduled releases task")
    
    try:
        # Run the scheduled task
        result = run_scheduled_releases()
        return jsonify({
            "status": "success",
            "message": "Scheduled releases task completed successfully",
            "details": result
        }), 200
    except Exception as e:
        logger.error(f"Error running scheduled task: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Scheduled task failed: {str(e)}"
        }), 500