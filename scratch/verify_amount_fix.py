import os
import re
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat

# Settings
pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = False
pipeline_options.do_table_structure = True 
converter = DocumentConverter(
    format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
)

def extract_total_test(text):
    total_amount = None
    # Priority 1: Row-aware Table Search
    total_rows = re.findall(r"\|\s*(?:TOTAL|GRAND TOTAL|TOTAL AMOUNT|PAYABLE|AMOUNT CHARGEABLE)\s*\|(.*)", text, re.IGNORECASE)
    if total_rows:
        for row_content in reversed(total_rows):
            clean_row = row_content.split("\n")[0]
            numbers_in_row = re.findall(r"([\d,]+\.\d{2}|[\d,]+)", clean_row)
            if numbers_in_row:
                 total_amount = numbers_in_row[-1].replace(",", "")
                 break
    
    # Priority 2: Label-Value patterns
    if not total_amount:
        label_matches = re.findall(r"(?:Total|Grand Total|Payable Amount|Amount Chargeable)\s*(?:[:\s|₹])*([\d,]+\.\d{2}|[\d,]+)", text, re.IGNORECASE)
        if label_matches:
             total_amount = label_matches[-1].replace(",", "")

    # Priority 3: Fallback
    if not total_amount:
        table_vals = re.findall(r"\|\s*([\d,]+\.\d{2})\s*\|", text)
        if table_vals:
            for val in reversed(table_vals):
                try:
                    clean_val = val.replace(",", "")
                    if float(clean_val) > 1.0:
                        total_amount = clean_val
                        break
                except: continue

    # Normalization
    if total_amount:
        try:
             amt_float = float(total_amount.replace(",", ""))
             return f"{amt_float:.2f}"
        except:
             return None
    return None

def run_test(file_path):
    print(f"\nTesting: {os.path.basename(file_path)}")
    result = converter.convert(file_path)
    text = result.document.export_to_markdown()
    extracted = extract_total_test(text)
    print(f"Extracted Total: {extracted}")

if __name__ == "__main__":
    files = [
        r"d:\Workspace\prince\setx_gsta4_hsn_itemsales invoice addition a t-1393 dated 28-mar-2026 202-r5090.pdf",
        r"d:\Workspace\prince\Sales Invoice T-589 Dated  8-8-2025.pdf"
    ]
    for f in files:
        if os.path.exists(f):
            run_test(f)
