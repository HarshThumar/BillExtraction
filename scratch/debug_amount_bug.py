import os
import re
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat

# Setup Docling (replicating main.py logic)
pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = False
pipeline_options.do_table_structure = True 
converter = DocumentConverter(
    format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
)

def debug_extract(file_path):
    print(f"\n--- Debugging: {os.path.basename(file_path)} ---")
    result = converter.convert(file_path)
    text = result.document.export_to_markdown()
    
    # Show search patterns from main.py
    print("\n[Regex Search Results]")
    
    # Approach A: Total/Amount keywords
    amount_matches = re.findall(r"(?:Total|Amount|Grand Total)\s*[:\s]*([\d,]+(?:\.\d{2})?)", text, re.IGNORECASE)
    print(f"Amount Matches (Approach A): {amount_matches}")
    
    # Approach B: Table values
    table_vals = re.findall(r"\|\s*([\d,]+\.\d{2})\s*\|", text)
    print(f"Table Values (Approach B, last 5): {table_vals[-5:] if table_vals else 'None'}")

    # Show raw markdown around the end of tables
    print("\n[Markdown Snippet (Last 1000 chars)]")
    print(text[-1000:])

if __name__ == "__main__":
    files = [
        r"d:\Workspace\prince\setx_gsta4_hsn_itemsales invoice addition a t-1393 dated 28-mar-2026 202-r5090.pdf",
        r"d:\Workspace\prince\Sales Invoice T-589 Dated  8-8-2025.pdf"
    ]
    for f in files:
        if os.path.exists(f):
            debug_extract(f)
        else:
            print(f"File not found: {f}")
