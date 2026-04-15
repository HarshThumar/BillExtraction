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

def run_deep_debug(file_path):
    print(f"\nDeep Debug: {os.path.basename(file_path)}")
    result = converter.convert(file_path)
    text = result.document.export_to_markdown()
    
    total_rows = re.findall(r"\|\s*(?:TOTAL|GRAND TOTAL|TOTAL AMOUNT|PAYABLE|AMOUNT CHARGEABLE)\s*\|(.*)", text, re.IGNORECASE)
    print(f"Total Rows found: {len(total_rows)}")
    for i, row in enumerate(total_rows):
        clean_row = row.split("\n")[0]
        numbers = re.findall(r"([\d,]+\.\d{2}|[\d,]+)", clean_row)
        print(f"Match {i}: Row='{clean_row}' | Numbers={numbers}")

if __name__ == "__main__":
    file = r"d:\Workspace\prince\setx_gsta4_hsn_itemsales invoice addition a t-1393 dated 28-mar-2026 202-r5090.pdf"
    if os.path.exists(file):
        run_deep_debug(file)
