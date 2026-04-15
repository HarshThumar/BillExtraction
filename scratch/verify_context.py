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

def extract_total_contextual(text):
    candidates = []
    lines = text.split("\n")
    for i, line in enumerate(lines):
        line_upper = line.upper()
        if any(k in line_upper for k in ["TOTAL", "GRAND TOTAL", "PAYABLE", "AMOUNT", "ROUND OFF"]):
            start = max(0, i - 2)
            end = min(len(lines), i + 3)
            context = " ".join(lines[start:end])
            nums = re.findall(r"([\d,]+\.\d{2}|[\d,]+)", context)
            for n in nums:
                try:
                    amt = float(n.replace(",", ""))
                    score = 100 if any(k in line_upper for k in ["GRAND", "PAYABLE", "AMOUNT"]) else 80
                    candidates.append((amt, score))
                except: pass

    # Proximity Search
    prox_matches = re.findall(r"(?:TOTAL|GRAND TOTAL|PAYABLE|AMOUNT CHARGEABLE).{0,150}?([\d,]+\.\d{2}|[\d,]+)", text, re.IGNORECASE | re.DOTALL)
    for match in prox_matches:
        try:
            candidates.append((float(match.replace(",", "")), 60))
        except: pass

    # Doc-wide Max Fallback
    all_numeric = re.findall(r"(?:₹|\s)*([\d,]+\.\d{2}|[\d,]{3,})", text)
    for val in all_numeric:
        try:
            amt_float = float(val.replace(",", ""))
            is_pincode = (amt_float.is_integer() and 100000 <= amt_float <= 999999)
            if 1.0 < amt_float < 10000000 and not is_pincode:
                candidates.append((amt_float, 10))
        except: pass

    if candidates:
        candidates.sort(key=lambda x: (x[1], x[0]), reverse=True)
        return f"{candidates[0][0]:.2f}"
    return None

def run_test(file_path):
    print(f"\nContextual Test: {os.path.basename(file_path)}")
    result = converter.convert(file_path)
    text = result.document.export_to_markdown()
    extracted = extract_total_contextual(text)
    print(f"Extracted Total: {extracted}")

if __name__ == "__main__":
    files = [
        r"d:\Workspace\prince\setx_gsta4_hsn_itemsales invoice addition a t-1393 dated 28-mar-2026 202-r5090.pdf",
        r"d:\Workspace\prince\Sales Invoice T-589 Dated  8-8-2025.pdf"
    ]
    for f in files:
        if os.path.exists(f):
            run_test(f)
