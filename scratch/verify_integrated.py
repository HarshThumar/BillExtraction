import os
import re
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat

# Settings
pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = True 
pipeline_options.do_table_structure = True 
converter = DocumentConverter(
    format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
)

def extract_total_integrated(text):
    candidates = []
    
    # 1. Line-by-line Search
    for line in text.split("\n"):
        if any(k in line.upper() for k in ["TOTAL", "GRAND TOTAL", "PAYABLE", "CHARGEABLE", "ROUND OFF"]):
            nums = re.findall(r"([\d,]+\.\d{2}|[\d,]+)", line)
            for n in nums:
                candidates.append(n.replace(",", ""))

    # 2. Proximity Search
    prox_matches = re.findall(r"(?:TOTAL|GRAND TOTAL|PAYABLE|AMOUNT CHARGEABLE).{0,150}?([\d,]+\.\d{2}|[\d,]+)", text, re.IGNORECASE | re.DOTALL)
    for match in prox_matches:
        candidates.append(match.replace(",", ""))

    # 3. Document-wide Scan
    all_numeric = re.findall(r"(?:₹|\s)*([\d,]+\.\d{2}|[\d,]{3,})", text)
    for val in all_numeric:
        candidates.append(val.replace(",", ""))

    # Final scoring
    best_amt = 0.0
    for val in candidates:
        try:
            amt_float = float(val.replace(",", ""))
            is_pincode = (amt_float.is_integer() and 100000 <= amt_float <= 999999)
            if 1.0 < amt_float < 10000000 and not is_pincode:
                if amt_float > best_amt:
                    best_amt = amt_float
        except: continue
        
    if best_amt > 0:
        return f"{best_amt:.2f}"
    return None

def run_test(file_path):
    print(f"\nIntegrated Test: {os.path.basename(file_path)}")
    result = converter.convert(file_path)
    text = result.document.export_to_markdown()
    extracted = extract_total_integrated(text)
    print(f"Extracted Total: {extracted}")

if __name__ == "__main__":
    files = [
        r"d:\Workspace\prince\setx_gsta4_hsn_itemsales invoice addition a t-1393 dated 28-mar-2026 202-r5090.pdf",
        r"d:\Workspace\prince\Sales Invoice T-589 Dated  8-8-2025.pdf"
    ]
    for f in files:
        if os.path.exists(f):
            run_test(f)
