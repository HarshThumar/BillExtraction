import re
text = "|          | Total                                         |           |         45 |       |        |       ₹ | 47,702.00 |"
match = re.search(r"\|\s*(?:TOTAL|GRAND TOTAL|TOTAL AMOUNT|PAYABLE|AMOUNT CHARGEABLE)\s*\|(.*)", text, re.IGNORECASE)
if match:
    row_content = match.group(1).split("\n")[0]
    print(f"Row content: '{row_content}'")
    numbers_in_row = re.findall(r"([\d,]+\.\d{2}|[\d,]+)", row_content)
    print(f"Numbers in row: {numbers_in_row}")
    if numbers_in_row:
        print(f"Final: {numbers_in_row[-1].replace(',', '')}")
