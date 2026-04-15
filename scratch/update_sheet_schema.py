import os
import gspread
import logging
from dotenv import load_dotenv
from google.auth import default, impersonated_credentials

# Load environment variables
load_dotenv(dotenv_path="backend-extraction/.env")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_sheets_client():
    creds, project = default()
    target_account = os.getenv("IMPERSONATED_SERVICE_ACCOUNT")
    
    if target_account:
        creds = impersonated_credentials.Credentials(
            source_credentials=creds,
            target_principal=target_account,
            target_scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ],
        )
    
    return gspread.authorize(creds)

def update_headers():
    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    if not sheet_id:
        print("GOOGLE_SHEET_ID missing!")
        return

    client = get_sheets_client()
    sheet = client.open_by_key(sheet_id).sheet1
    
    headers = [
        "Buyer Name", 
        "Buyer Address", 
        "GST No", 
        "Mobile No", 
        "Bill No", 
        "Date", 
        "Total Amount", 
        "Extraction Time", 
        "Status", 
        "WhatsApp (EN)", 
        "WhatsApp (GJ)"
    ]
    
    # Update the first row
    sheet.update('A1:K1', [headers])
    print(f"Successfully updated headers in sheet: {sheet_id}")

if __name__ == "__main__":
    update_headers()
