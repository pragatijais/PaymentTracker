from bs4 import BeautifulSoup
import re
from datetime import datetime

def parse_google_pay_html(html_file):
    # Read the HTML file
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Find where the head section ends
    head_end = html_content.find('</head>')
    if head_end == -1:
        return []
    
    # Get the content after </head>
    content_after_head = html_content[head_end + 7:]  # 7 is length of '</head>'
    
    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(content_after_head, 'html.parser')
    
    # Find all transaction entries
    transactions = []
    
    # Look for transaction entries in the HTML
    # Note: You may need to adjust these selectors based on the actual HTML structure
    for entry in soup.find_all('div', class_='mdl-list__item'):
        transaction = {}
        
        # Extract date and time
        date_time = entry.find('div', class_='mdl-list__item-secondary-content')
        if date_time:
            date_time_text = date_time.get_text(strip=True)
            # Try to parse date and time
            try:
                # Adjust the date format pattern based on your HTML
                dt = datetime.strptime(date_time_text, '%b %d, %Y, %I:%M:%S %p')
                transaction['date'] = dt.strftime('%Y-%m-%d')
                transaction['time'] = dt.strftime('%H:%M:%S')
            except ValueError:
                transaction['date'] = date_time_text
                transaction['time'] = ''
        
        # Extract amount
        amount = entry.find('div', class_='mdl-list__item-primary-content')
        if amount:
            amount_text = amount.get_text(strip=True)
            # Look for amount pattern (e.g., ₹1,000.00)
            amount_match = re.search(r'₹([\d,]+\.?\d*)', amount_text)
            if amount_match:
                transaction['amount'] = amount_match.group(1)
        
        # Extract credited to
        credited_to = entry.find('div', class_='mdl-list__item-sub-title')
        if credited_to:
            transaction['credited_to'] = credited_to.get_text(strip=True)
        
        # Extract remarks
        remarks = entry.find('div', class_='mdl-list__item-text-body')
        if remarks:
            transaction['remarks'] = remarks.get_text(strip=True)
        
        if transaction:
            transactions.append(transaction)
    
    return transactions

def main():
    html_file = 'My Activity.html'
    transactions = parse_google_pay_html(html_file)
    
    # Print the extracted information
    for i, trans in enumerate(transactions, 1):
        print(f"\nTransaction {i}:")
        print(f"Date: {trans.get('date', 'N/A')}")
        print(f"Time: {trans.get('time', 'N/A')}")
        print(f"Amount: ₹{trans.get('amount', 'N/A')}")
        print(f"Credited to: {trans.get('credited_to', 'N/A')}")
        print(f"Remarks: {trans.get('remarks', 'N/A')}")

if __name__ == "__main__":
    main() 