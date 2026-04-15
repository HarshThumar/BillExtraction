import os
import re
import logging
import gspread # type: ignore
from datetime import datetime
from typing import Optional, List

from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google.auth import default, impersonated_credentials # type: ignore
from urllib.parse import quote

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

logger.info("Initializing Invoice Extraction API...")

from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption

# Initialize Docling Converter
# Enabled OCR for robustness with diverse invoice layouts
pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = True
pipeline_options.do_table_structure = True 

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)

app = FastAPI(
    title="Invoice Extraction API",
    description="Backend for high-precision invoice extraction using Docling.",
    version="1.0.0"
)

# Enable CORS for frontend communication
# In production, restrict 'allow_origins' to your Firebase domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class InvoiceData(BaseModel):
    buyer_name: Optional[str] = None
    buyer_address: Optional[str] = None
    gst_no: Optional[str] = None
    mobile_no: Optional[str] = None
    bill_no: Optional[str] = None
    date: Optional[str] = None
    total_amount: Optional[str] = None

def get_sheets_client():
    """Returns a gspread client, optionally using service account impersonation."""
    try:
        creds, project = default()
        target_account = os.getenv("IMPERSONATED_SERVICE_ACCOUNT")
        
        if target_account:
            logger.info(f"Using impersonated identity: {target_account}")
            creds = impersonated_credentials.Credentials(
                source_credentials=creds,
                target_principal=target_account,
                target_scopes=[
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive"
                ],
            )
        
        return gspread.authorize(creds)
    except Exception as e:
        logger.error(f"Failed to initialize Google Auth: {e}")
        raise

def extract_fields(text: str) -> InvoiceData:
    """Robust logic to map text patterns to invoice fields using section awareness."""
    data = InvoiceData()
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    
    # 1. Identify Sections
    receiver_section = []
    in_receiver = False
    for line in lines:
        if "Details of Receiver" in line or "Buyer Details" in line:
            in_receiver = True
            continue
        if in_receiver:
            # End section if another major header or Table data starts
            if line.startswith("##") or "|--" in line or "Sr. No" in line:
                break
            receiver_section.append(line)

    # 2. Extract Buyer Name and Address from Receiver Section
    if receiver_section:
        logger.info(f"Inferred Receiver Section: {receiver_section}")
        # Look for the name (often the first thing or after a label)
        for i, line in enumerate(receiver_section):
            # Known entities fallback
            if "HAPPY ENTERPRISE" in line or "OM REFRIGERATION" in line:
                data.buyer_name = line.split(":")[0].strip() if ":" in line else line.strip()
                break
            
            if not data.buyer_name and i < 4 and len(line) > 5 and "Details" not in line and "Invoice" not in line:
                # Heuristic: First long-ish line without many numbers/symbols is the name
                if not any(c.isdigit() for c in line[:5]):
                    data.buyer_name = line.split(":")[0].strip() if ":" in line else line.strip()
                    break

        # Address: Lines following the name that look like address parts
        if data.buyer_name:
            addr_parts = []
            found_name = False
            for line in receiver_section:
                clean_line = line.split(":")[0].strip() if ":" in line else line.strip()
                if clean_line == data.buyer_name:
                    found_name = True
                    continue
                if found_name:
                    if any(key in line for key in ["GSTIN", "Phone", "State", "Mob", "UIN"]):
                        break
                    addr_parts.append(clean_line)
            if addr_parts:
                data.buyer_address = ", ".join(addr_parts)

    # 3. GST No (Prioritize Receiver section, then global)
    gst_pattern = r"[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}"
    if receiver_section:
        for line in receiver_section:
            match = re.search(gst_pattern, line)
            if match:
                data.gst_no = match.group(0)
                break
    
    if not data.gst_no:
        gst_matches = re.findall(gst_pattern, text)
        if gst_matches:
            # The last match is often the Buyer's GST in common formats
            data.gst_no = gst_matches[-1]

    # 4. Mobile No
    # Look for 10 digit numbers, prioritize those starting with 6-9
    mobile_pattern = r"(?:Phone|Mob|Mo)\.?\s*[:\n]*\s*(\d{10})"
    mobile_match = re.search(mobile_pattern, "\n".join(receiver_section), re.IGNORECASE)
    if not mobile_match:
        mobile_match = re.search(mobile_pattern, text, re.IGNORECASE)
        
    if mobile_match:
        data.mobile_no = mobile_match.group(1)
    else:
        # Generic 10 digit fallback
        all_numbers = re.findall(r"([6-9]\d{9})", text)
        if all_numbers:
            data.mobile_no = all_numbers[0]

    # 5. Bill No
    # Priority 1: Specific recognized patterns (e.g., T/1393, A/102)
    specific_pattern = re.search(r"\b[A-Z]/[0-9]{2,}\b", text)
    if specific_pattern:
        data.bill_no = specific_pattern.group(0)
    
    # Priority 2: Label based lookup
    if not data.bill_no:
        bill_no_match = re.search(r"(?:Invoice Number|Bill No|Inv No)\s*[:\n]*\s*([A-Z0-9/\\-]+)", text, re.IGNORECASE)
        if bill_no_match:
            val = bill_no_match.group(1).strip()
            # If the value is part of the buyer name, it's likely a mis-match
            if data.buyer_name and (val.upper() in data.buyer_name.upper() or data.buyer_name.upper() in val.upper()):
                pass 
            elif len(val) > 1:
                data.bill_no = val

    # 6. Date
    # Look for dates in formats DD/MM/YYYY or DD-MM-YYYY
    date_matches = re.findall(r"(\d{2}/\d{2}/\d{4}|\d{2}-\d{2}-\d{4})", text)
    if date_matches:
        # Usually the first date is the Invoice Date
        data.date = date_matches[0]

    # Final Total Amount Extraction Logic
    # We iterate backwards through the document lines to find the LAST "Total" row,
    # which is almost always the Grand Total in Indian GST invoices.
    lines = text.split("\n")
    for i in range(len(lines) - 1, -1, -1):
        line_upper = lines[i].upper()
        if any(k in line_upper for k in ["TOTAL AMOUNT", "GRAND TOTAL", "PAYABLE", "AMOUNT CHARGEABLE", "TOTAL"]):
            # Look for a number in this line or the immediate lines around it
            start = max(0, i - 1)
            end = min(len(lines), i + 2)
            context = " ".join(lines[start:end])
            
            # Find all numeric strings in this context
            nums = re.findall(r"([\d,]+\.\d{2}|[\d,]+)", context)
            if nums:
                valid_candidates = []
                for n in nums:
                    try:
                        amt = float(n.replace(",", ""))
                        amt_int_str = str(int(amt))
                        # Filters:
                        # 1. Reasonable range (1.0 to 2M)
                        # 2. Not a Pincode (exactly 6 digits integer)
                        # 3. Not an A/C number (>= 10 digits)
                        is_pincode = (amt.is_integer() and len(amt_int_str) == 6)
                        if 1.0 < amt < 2000000 and not is_pincode and len(amt_int_str) < 10:
                            valid_candidates.append(amt)
                    except: continue
                
                if valid_candidates:
                    # Grand total is usually the largest number in the final "Total" area
                    data.total_amount = f"{max(valid_candidates):.2f}"
                    return data

    return data

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/extract", response_model=InvoiceData)
async def extract_invoice(file: UploadFile = File(...)):
    """Receives a PDF, converts it to markdown using Docling, and extracts fields."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    temp_path = f"temp_{file.filename}"
    logger.info(f"Processing file: {file.filename}")
    
    with open(temp_path, "wb") as f:
        f.write(await file.read())
    
    try:
        result = converter.convert(temp_path)
        text_content = result.document.export_to_markdown()
        logger.info(f"Markdown Content:\n{text_content[:500]}...")
        extracted_data = extract_fields(text_content)
        logger.info(f"Extraction successful for {file.filename}")
        return extracted_data
    except Exception as e:
        logger.exception(f"Extraction failed for {file.filename}")
        raise HTTPException(status_code=500, detail="Document processing failed")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.post("/save")
async def save_to_sheet(data: InvoiceData):
    """Appends extracted data as a new row in Google Sheets."""
    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    if not sheet_id:
        logger.error("GOOGLE_SHEET_ID is missing from environment")
        raise HTTPException(status_code=500, detail="Sheet ID not configured")
    
    try:
        client = get_sheets_client()
        sheet = client.open_by_key(sheet_id).sheet1
        
        # Clean phone number (keep only digits, ensure 91 prefix for 10-digit numbers)
        phone = re.sub(r"\D", "", data.mobile_no or "")
        if len(phone) == 10:
            phone = "91" + phone
            
        whatsapp_en = ""
        whatsapp_gj = ""
        
        if phone:
            # English Template
            msg_en = f"Hi {data.buyer_name or 'Customer'}, your bill of ₹{data.total_amount or '0'} is ready. (Bill No: {data.bill_no or 'N/A'}). Thank you!"
            url_en = f"https://wa.me/{phone}?text={quote(msg_en)}"
            whatsapp_en = f'=HYPERLINK("{url_en}", "Message (EN)")'
            
            # Gujarati Template
            msg_gj = f"નમસ્તે {data.buyer_name or 'Customer'}, તમારું ₹{data.total_amount or '0'} નું બિલ તૈયાર છે. (બિલ નંબર: {data.bill_no or 'N/A'}). આભાર!"
            url_gj = f"https://wa.me/{phone}?text={quote(msg_gj)}"
            whatsapp_gj = f'=HYPERLINK("{url_gj}", "Message (GJ)")'

        row = [
            data.buyer_name,
            data.buyer_address,
            data.gst_no,
            data.mobile_no,
            data.bill_no,
            data.date,
            data.total_amount,
            datetime.now().isoformat(),
            "Pending",
            whatsapp_en,
            whatsapp_gj
        ]
        
        sheet.append_row(row, value_input_option='USER_ENTERED')
        logger.info("Successfully appended row to Google Sheet")
        return {"success": True}
    except Exception as e:
        logger.exception("Failed to save to Google Sheet")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/save-bulk")
async def save_bulk(data: List[InvoiceData]):
    """Appends multiple extracted data records to Google Sheets in a single batch."""
    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    if not sheet_id:
        logger.error("GOOGLE_SHEET_ID is missing from environment")
        raise HTTPException(status_code=500, detail="Sheet ID not configured")
    
    try:
        client = get_sheets_client()
        sheet = client.open_by_key(sheet_id).sheet1
        
        rows_to_append = []
        for item in data:
            # Clean phone number (duplicated logic for safety, could be refactored)
            phone = re.sub(r"\D", "", item.mobile_no or "")
            if len(phone) == 10:
                phone = "91" + phone
                
            whatsapp_en = ""
            whatsapp_gj = ""
            
            if phone:
                # English Template
                msg_en = f"Hi {item.buyer_name or 'Customer'}, your bill of ₹{item.total_amount or '0'} is ready. (Bill No: {item.bill_no or 'N/A'}). Thank you!"
                url_en = f"https://wa.me/{phone}?text={quote(msg_en)}"
                whatsapp_en = f'=HYPERLINK("{url_en}", "Message (EN)")'
                
                # Gujarati Template
                msg_gj = f"નમસ્તે {item.buyer_name or 'Customer'}, તમારું ₹{item.total_amount or '0'} નું બિલ તૈયાર છે. (બિલ નંબર: {item.bill_no or 'N/A'}). આભાર!"
                url_gj = f"https://wa.me/{phone}?text={quote(msg_gj)}"
                whatsapp_gj = f'=HYPERLINK("{url_gj}", "Message (GJ)")'

            rows_to_append.append([
                item.buyer_name,
                item.buyer_address,
                item.gst_no,
                item.mobile_no,
                item.bill_no,
                item.date,
                item.total_amount,
                datetime.now().isoformat(),
                "Pending",
                whatsapp_en,
                whatsapp_gj
            ])
            
        if rows_to_append:
            sheet.append_rows(rows_to_append, value_input_option='USER_ENTERED')
            logger.info(f"Successfully appended {len(rows_to_append)} rows to Google Sheet")
            
        return {"success": True, "count": len(rows_to_append)}
    except Exception as e:
        logger.exception("Failed to save bulk to Google Sheet")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting server on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
