import os
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption

def debug_extraction():
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = False
    pipeline_options.do_table_structure = True 

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    pdf_path = r"d:\Workspace\prince\setx_gsta4_hsn_itemsales invoice addition a t-1393 dated 28-mar-2026 202-r5090.pdf"
    result = converter.convert(pdf_path)
    md_text = result.document.export_to_markdown()
    
    print("--- Docling Markdown Output ---")
    print(md_text)
    print("-------------------------------")

if __name__ == "__main__":
    debug_extraction()
