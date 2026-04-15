import re
from urllib.parse import quote

class MockInvoiceData:
    def __init__(self, buyer_name, mobile_no, total_amount, bill_no):
        self.buyer_name = buyer_name
        self.mobile_no = mobile_no
        self.total_amount = total_amount
        self.bill_no = bill_no

data = MockInvoiceData("Rajesh Kumar", "9876543210", "1500.00", "T-1393")

# Logic from main.py
phone = re.sub(r"\D", "", data.mobile_no or "")
if len(phone) == 10:
    phone = "91" + phone
    
whatsapp_en = ""
whatsapp_gj = ""

if phone:
    # English Template
    msg_en = f"Hi {data.buyer_name or 'Customer'}, your bill of ₹{data.total_amount or '0'} is ready. (Bill No: {data.bill_no or 'N/A'}). Thank you!"
    url_en = f"https://wa.me/{phone}?text={quote(msg_en)}"
    whatsapp_en = f'=HYPERLINK("{url_en}", "Message (EN)")'
    
    # Gujarati Template
    msg_gj = f"નમસ્તે {data.buyer_name or 'Customer'}, તમારું ₹{data.total_amount or '0'} નું બિલ તૈયાર છે. (બિલ નંબર: {data.bill_no or 'N/A'}). આભાર!"
    url_gj = f"https://wa.me/{phone}?text={quote(msg_gj)}"
    whatsapp_gj = f'=HYPERLINK("{url_gj}", "Message (GJ)")'

print(f"Phone: {phone}")
print(f"WhatsApp EN: {whatsapp_en}")
print(f"WhatsApp GJ: {whatsapp_gj}")
