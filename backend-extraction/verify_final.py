import os
import sys
import re

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import extract_fields, converter

def verify_robust_extraction():
    pdf_path = r"d:\Workspace\prince\setx_gsta4_hsn_itemsales invoice addition a t-1393 dated 28-mar-2026 202-r5090.pdf"
    
    print(f"Loading and converting: {pdf_path}")
    result = converter.convert(pdf_path)
    text_content = result.document.export_to_markdown()
    
    print("\n--- Raw Markdown (First 1000 chars) ---")
    print(text_content[:1000])
    
    print("\n--- Running Robust Extraction ---")
    data = extract_fields(text_content)
    
    print(f"Buyer Name:    {data.buyer_name}")
    print(f"Buyer Address: {data.buyer_address}")
    print(f"GST No:        {data.gst_no}")
    print(f"Mobile No:     {data.mobile_no}")
    print(f"Bill No:       {data.bill_no}")
    print(f"Date:          {data.date}")
    print(f"Total Amount:  {data.total_amount}")
    
    # Assertions
    if data.buyer_name == "HAPPY ENTERPRISE" and data.bill_no == "T/1393":
        print("\n✅ Verification Successful!")
    else:
        print("\n❌ Verification Failed (Check Name or Bill No)")

if __name__ == "__main__":
    verify_robust_extraction()
