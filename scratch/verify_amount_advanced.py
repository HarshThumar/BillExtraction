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

def extract_total_advanced(text):
    candidates = []
    
    # 1. Row-aware Table Search (Last number in a Total row)
    total_rows = re.findall(r"\|\s*(?:TOTAL|GRAND TOTAL|TOTAL AMOUNT|PAYABLE|AMOUNT CHARGEABLE)\s*\|(.*)", text, re.IGNORECASE)
    for row in total_rows:
        row_clean = row.split("\n")[0]
        nums = re.findall(r"([\d,]+\.\d{2}|[\d,]+)", row_clean)
        if nums:
            candidates.append(nums[-1].replace(",", ""))

    # 2. Proximity Search (Label followed by number within 100 chars)
    # This handles multiline wrapping or weird table artifacts
    prox_matches = re.findall(r"(?:TOTAL|GRAND TOTAL|PAYABLE|AMOUNT CHARGEABLE).{0,100}?([\d,]+\.\d{2}|[\d,]+)", text, re.IGNORECASE | re.DOTALL)
    for match in prox_matches:
        candidates.append(match.replace(",", ""))

    # 3. Large values at the end of tables
    table_vals = re.findall(r"\|\s*([\d,]+\.\d{2})\s*\|", text)
    if table_vals:
        candidates.append(table_vals[-1].replace(",", ""))

    # Filter and Rank Candidates
    final_candidates = []
    for val in candidates:
        try:
            amt = float(val)
            # Filter out dates (usually current year/past year) and GSTIN parts
            if 1.0 < amt < 10000000 and len(val.replace(".", "")) < 12:
                final_candidates.append(amt)
        except: continue
    
    if final_candidates:
        # Usually the largest value among these candidates is the Grand Total
        # (Beats subtotals, tax components, and quantity)
        return f"{max(final_candidates):.2f}"
    
    return None

def run_test(file_path):
    print(f"\nAdvanced Test: {os.path.basename(file_path)}")
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
