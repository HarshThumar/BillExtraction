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

def extract_total_last(text):
    lines = text.split("\n")
    for i in range(len(lines) - 1, -1, -1):
        line_upper = lines[i].upper()
        if any(k in line_upper for k in ["TOTAL AMOUNT", "GRAND TOTAL", "PAYABLE", "AMOUNT CHARGEABLE", "TOTAL"]):
            start = max(0, i - 1)
            end = min(len(lines), i + 2)
            context = " ".join(lines[start:end])
            nums = re.findall(r"([\d,]+\.\d{2}|[\d,]+)", context)
            if nums:
                valid_candidates = []
                for n in nums:
                    try:
                        amt = float(n.replace(",", ""))
                        amt_int_str = str(int(amt))
                        is_pincode = (amt.is_integer() and len(amt_int_str) == 6)
                        if 1.0 < amt < 2000000 and not is_pincode and len(amt_int_str) < 10:
                            valid_candidates.append(amt)
                    except: continue
                if valid_candidates:
                    return f"{max(valid_candidates):.2f}"
    return None

def run_test(file_path):
    print(f"\nLast Total Test: {os.path.basename(file_path)}")
    result = converter.convert(file_path)
    text = result.document.export_to_markdown()
    extracted = extract_total_last(text)
    print(f"Extracted Total: {extracted}")

if __name__ == "__main__":
    files = [
        r"d:\Workspace\prince\setx_gsta4_hsn_itemsales invoice addition a t-1393 dated 28-mar-2026 202-r5090.pdf",
        r"d:\Workspace\prince\Sales Invoice T-589 Dated  8-8-2025.pdf"
    ]
    for f in files:
        if os.path.exists(f):
            run_test(f)
