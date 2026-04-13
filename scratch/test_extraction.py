import requests

url = "http://localhost:8000/extract"
file_path = r"d:\Workspace\prince\Sales Invoice T-589 Dated  8-8-2025.pdf"

with open(file_path, "rb") as f:
    files = {"file": f}
    response = requests.post(url, files=files)

print(response.status_code)
print(response.json())
