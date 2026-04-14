import os
import logging
import gspread # type: ignore
from google.auth import default, impersonated_credentials # type: ignore
from google.oauth2 import id_token # type: ignore
from google.auth.transport.requests import Request # type: ignore
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

def check_sheet_access():
    # 1. Load environment variables
    load_dotenv()
    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    target_account = os.getenv("IMPERSONATED_SERVICE_ACCOUNT")
    
    if not sheet_id:
        logger.error("GOOGLE_SHEET_ID not found in environment variables.")
        return

    logger.info(f"Target Sheet ID: {sheet_id}")

    try:
        # 2. Get Source Credentials (ADC)
        creds, project = default(
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
                "https://www.googleapis.com/auth/cloud-platform"
            ]
        )
        
        # Log who we are currently
        if hasattr(creds, 'service_account_email'):
             logger.info(f"Source Identity: {creds.service_account_email}")
        else:
             logger.info("Source Identity: Local User (gcloud ADC)")

        # 3. Apply Impersonation if configured
        if target_account:
            logger.info(f"Attempting to impersonate: {target_account}")
            creds = impersonated_credentials.Credentials(
                source_credentials=creds,
                target_principal=target_account,
                target_scopes=[
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive"
                ],
            )
        
        # 4. Authorize gspread
        client = gspread.authorize(creds)

        # 5. Try to open the sheet
        spreadsheet = client.open_by_key(sheet_id)
        sheet_title = spreadsheet.title
        logger.info(f"✅ SUCCESS! Successfully accessed spreadsheet: '{sheet_title}'")
        
    except Exception as e:
        logger.error("❌ Failed to access sheet.")
        error_msg = str(e)
        logger.error(f"Error Detail: {error_msg}")
        
        if "SERVICE_DISABLED" in error_msg or "iamcredentials.googleapis.com" in error_msg:
             logger.warning("!!! ACTION REQUIRED: The 'IAM Service Account Credentials API' is disabled.")
             logger.warning("Please run: gcloud services enable iamcredentials.googleapis.com --project=bigquery-sandbox-450906")
        elif "PERMISSION_DENIED" in error_msg:
             logger.warning("!!! IAM PROPAGATION: If you just ran the grant command, wait 60 seconds and try again.")
        
if __name__ == "__main__":
    check_sheet_access()
