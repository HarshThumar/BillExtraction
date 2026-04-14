import os
from dotenv import load_dotenv
import gspread
from google.auth import default
from google.auth.impersonated_credentials import Credentials as ImpersonatedCredentials

# Load environment variables
load_dotenv(os.path.join("backend-extraction", ".env"))

# Configuration
SPREADSHEET_ID = os.getenv("GOOGLE_SHEET_ID", "1ESpXPrhesyxgD9WELxtf0es9WU742iZXPlnXrg-YuE0")
TARGET_SERVICE_ACCOUNT = "prince-deployer@soulmate-tours.iam.gserviceaccount.com"

def get_impersonated_client():
    # 1. Get Application Default Credentials (as the user)
    print("Fetching Application Default Credentials...")
    creds, project_id = default()
    
    # 2. Create Impersonated Credentials
    print(f"Requesting impersonated credentials for: {TARGET_SERVICE_ACCOUNT}")
    impersonated_creds = ImpersonatedCredentials(
        source_credentials=creds,
        target_principal=TARGET_SERVICE_ACCOUNT,
        target_scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"],
    )
    
    # 3. Use with gspread
    client = gspread.authorize(impersonated_creds)
    return client

def test_read_sheet():
    try:
        client = get_impersonated_client()
        
        print(f"Opening spreadsheet: {SPREADSHEET_ID}...")
        spreadsheet = client.open_by_key(SPREADSHEET_ID)
        
        # Select first worksheet
        worksheet = spreadsheet.get_worksheet(0)
        
        print(f"Reading data from worksheet: {worksheet.title}...")
        # Get all records or first few rows
        data = worksheet.get_all_values()
        
        if data:
            print("\nSuccessfully read data from sheet!")
            print("First row:", data[0])
            if len(data) > 1:
                print("Second row:", data[1])
        else:
            print("\nSheet is empty, but access is confirmed!")
            
    except Exception as e:
        print(f"\nError testing sheet access: {e}")
        print("\nPossible issues:")
        print("1. Sheet not shared with the service account email.")
        print("2. 'Service Account Token Creator' role not yet propagated (takes a minute).")
        print("3. ADC not set up correctly (run 'gcloud auth application-default login').")

if __name__ == "__main__":
    test_read_sheet()
