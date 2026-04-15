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

def extract_total_weighted(text):
    candidates = []
    
    # 1. Row-aware Search
    for line in text.split("\n"):
        line_upper = line.upper()
        if any(k in line_upper for k in ["GRAND TOTAL", "PAYABLE", "AMOUNT CHARGEABLE", "TOTAL AMOUNT"]):
            nums = re.findall(r"([\d,]+\.\d{2}|[\d,]+)", line)
            if nums:
                try:
                    candidates.append((float(nums[-1].replace(",", "")), 100))
                except: pass
        elif "TOTAL" in line_upper or "ROUND OFF" in line_upper:
            nums = re.findall(r"([\d,]+\.\d{2}|[\d,]+)", line)
            if nums:
                try:
                    candidates.append((float(nums[-1].replace(",", "")), 80))
                except: pass

    # 2. Proximity Search
    prox_matches = re.findall(r"(?:TOTAL|GRAND TOTAL|PAYABLE|AMOUNT CHARGEABLE).{0,150}?([\d,]+\.\d{2}|[\d,]+)", text, re.IGNORECASE | re.DOTALL)
    for match in prox_matches:
        try:
            candidates.append((float(match.replace(",", "")), 60))
        except: pass

    # 3. Doc-wide Max Fallback
    all_numeric = re.findall(r"(?:₹|\s)*([\d,]+\.\d{2}|[\d,]{3,})", text)
    for val in all_numeric:
        try:
            amt_float = float(val.replace(",", ""))
            is_pincode = (amt_float.is_integer() and 100000 <= amt_float <= 999999)
            if 1.0 < amt_float < 10000000 and not is_pincode:
                candidates.append((amt_float, 10))
        except: pass

    # Sort and Pick
    if candidates:
        candidates.sort(key=lambda x: (x[1], x[0]), reverse=True)
        return f"{candidates[0][0]:.2f}"
    return None

def run_test(file_path):
    print(f"\nWeighted Test: {os.path.basename(file_path)}")
    result = converter.convert(file_path)
    text = result.document.export_to_markdown()
    extracted = extract_total_weighted(text)
    print(f"Extracted Total: {extracted}")

if __name__ == "__main__":
    files = [
        r"d:\Workspace\prince\setx_gsta4_hsn_itemsales invoice addition a t-1393 dated 28-mar-2026 202-r5090.pdf",
        r"d:\Workspace\prince\Sales Invoice T-589 Dated  8-8-2025.pdf"
    ]
    for f in files:
        if os.path.exists(f):
            run_test(f)
