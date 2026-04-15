import os
import re
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat

# Settings - Matches main.py exactly
pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = True 
pipeline_options.do_table_structure = True 
converter = DocumentConverter(
    format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
)

def extract_total_advanced(text):
    candidates = []
    
    # 1. Line-by-line search
    for line in text.split("\n"):
        if any(k in line.upper() for k in ["TOTAL", "GRAND TOTAL", "PAYABLE", "CHARGEABLE"]):
            nums = re.findall(r"([\d,]+\.\d{2}|[\d,]+)", line)
            if nums:
                 candidates.append(nums[-1].replace(",", ""))

    # 2. Proximity Search (Handles wrapping or OCR offset)
    prox_matches = re.findall(r"(?:TOTAL|GRAND TOTAL|PAYABLE|AMOUNT CHARGEABLE).{0,150}?([\d,]+\.\d{2}|[\d,]+)", text, re.IGNORECASE | re.DOTALL)
    for match in prox_matches:
        candidates.append(match.replace(",", ""))

    # 3. Large values at the end of tables
    table_vals = re.findall(r"\|\s*([\d,]+\.\d{2})\s*\|", text)
    if table_vals:
        candidates.append(table_vals[-1].replace(",", ""))

    # Final scoring
    best_val = None
    max_amt = -1.0
    for val in candidates:
        try:
            amt_float = float(val.replace(",", ""))
            if 1.0 < amt_float < 10000000 and len(val.replace(".", "")) < 12:
                if amt_float > max_amt:
                    max_amt = amt_float
                    best_val = f"{amt_float:.2f}"
        except: continue
    
    return best_val

def run_test(file_path):
    print(f"\nTesting with OCR: {os.path.basename(file_path)}")
    result = converter.convert(file_path)
    text = result.document.export_to_markdown()
    extracted = extract_total_advanced(text)
    print(f"Extracted Total: {extracted}")

if __name__ == "__main__":
    files = [
        r"d:\Workspace\prince\setx_gsta4_hsn_itemsales invoice addition a t-1393 dated 28-mar-2026 202-r5090.pdf",
        r"d:\Workspace\prince\Sales Invoice T-589 Dated  8-8-2025.pdf"
    ]
    for f in files:
        if os.path.exists(f):
            run_test(f)
