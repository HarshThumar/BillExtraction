import os
from docling.document_converter import DocumentConverter

converter = DocumentConverter()

def search_for_value(file_path, value_str):
    print(f"\nSearching '{value_str}' in {os.path.basename(file_path)}")
    result = converter.convert(file_path)
    markdown = result.document.export_to_markdown()
    
    if value_str in markdown:
        print(f"FOUND string '{value_str}' in Markdown!")
        # Print surroundings
        idx = markdown.find(value_str)
        print(f"Context: ...{markdown[idx-50:idx+50]}...")
    else:
        print(f"NOT FOUND string '{value_str}' in Markdown.")
    
    # Check if it exists with commas
    value_with_commas = "47,702.00"
    if value_with_commas in markdown:
        print(f"FOUND string '{value_with_commas}' in Markdown!")
    else:
        print(f"NOT FOUND string '{value_with_commas}' in Markdown.")

if __name__ == "__main__":
    search_for_value(r"d:\Workspace\prince\setx_gsta4_hsn_itemsales invoice addition a t-1393 dated 28-mar-2026 202-r5090.pdf", "47702")
