import os
from docling.document_converter import DocumentConverter

converter = DocumentConverter()

def investigate(file_path):
    print(f"\nInvestigating: {os.path.basename(file_path)}")
    result = converter.convert(file_path)
    text = result.document.export_to_markdown()
    
    # Is 5133 in there?
    if "5133" in text:
        idx = text.find("5133")
        print(f"FOUND '5133'. Context: ...{text[idx-50:idx+50]}...")
    
    # Where is 4600?
    if "4600" in text:
        idx = text.find("4600")
        print(f"FOUND '4600'. Context: ...{text[idx-50:idx+50]}...")

if __name__ == "__main__":
    investigate(r"d:\Workspace\prince\Sales Invoice T-589 Dated  8-8-2025.pdf")
