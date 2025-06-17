import os
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import csv
import re

def parse_transaction_details(transaction_text, details_text):
    """
    Parse transaction text and details into structured data.
    
    Args:
        transaction_text (str): Main transaction text
        details_text (str): Transaction details text
        
    Returns:
        dict: Parsed transaction data
    """
    # Initialize transaction data
    transaction_data = {
        'date': None,
        'day': None,
        'type': None,
        'amount': None,
        'currency': None,
        'recipient': None,
        'status': None,
        'description': None
    }
    
    # Multiple date patterns to try
    date_patterns = [
        r'([A-Za-z]{3} \d{1,2}, \d{4}, \d{1,2}:\d{2}:\d{2} [AP]M GMT\+\d{2}:\d{2})',  # Jan 20, 2023, 4:36:02 PM GMT+05:30
        r'([A-Za-z]{3} \d{1,2}, \d{4}, \d{1,2}:\d{2} [AP]M GMT\+\d{2}:\d{2})',         # Jan 20, 2023, 4:36 PM GMT+05:30
        r'([A-Za-z]{3} \d{1,2}, \d{4}, \d{1,2}:\d{2}:\d{2} [AP]M)',                    # Jan 20, 2023, 4:36:02 PM
        r'([A-Za-z]{3} \d{1,2}, \d{4}, \d{1,2}:\d{2} [AP]M)',                          # Jan 20, 2023, 4:36 PM
        r'([A-Za-z]{3} \d{1,2}, \d{4})'                                                # Jan 20, 2023
    ]
    
    # Try each date pattern
    date_str = None
    for pattern in date_patterns:
        date_match = re.search(pattern, details_text) or re.search(pattern, transaction_text)
        if date_match:
            date_str = date_match.group(1)
            break
    
    if date_str:
        try:
            # Try different date formats
            date_formats = [
                '%b %d, %Y, %I:%M:%S %p GMT%z',  # Jan 20, 2023, 4:36:02 PM GMT+05:30
                '%b %d, %Y, %I:%M %p GMT%z',     # Jan 20, 2023, 4:36 PM GMT+05:30
                '%b %d, %Y, %I:%M:%S %p',        # Jan 20, 2023, 4:36:02 PM
                '%b %d, %Y, %I:%M %p',           # Jan 20, 2023, 4:36 PM
                '%b %d, %Y'                      # Jan 20, 2023
            ]
            
            date_obj = None
            for date_format in date_formats:
                try:
                    # Handle GMT offset format
                    if 'GMT' in date_str:
                        date_str = date_str.replace('GMT+', 'GMT+').replace('GMT-', 'GMT-')
                        date_str = date_str.replace(':', '')
                    date_obj = datetime.strptime(date_str, date_format)
                    break
                except ValueError:
                    continue
            
            if date_obj:
                transaction_data['date'] = date_obj.strftime('%Y-%m-%d %H:%M:%S')
                transaction_data['day'] = date_obj.strftime('%A')
        except Exception:
            pass
    
    # Extract amount and currency
    amount_match = re.search(r'([₹$€£])\s*([\d,]+\.?\d*)', transaction_text)
    if amount_match:
        transaction_data['currency'] = amount_match.group(1)
        transaction_data['amount'] = amount_match.group(2).replace(',', '')
    
    # Determine transaction type
    if 'paid' in transaction_text.lower():
        transaction_data['type'] = 'Payment'
    elif 'received' in transaction_text.lower():
        transaction_data['type'] = 'Receipt'
    elif 'sent' in transaction_text.lower():
        transaction_data['type'] = 'Transfer'
    
    # Extract recipient/sender
    recipient_match = re.search(r'(?:to|from)\s+([A-Za-z\s]+)', transaction_text)
    if recipient_match:
        transaction_data['recipient'] = recipient_match.group(1).strip()
    
    # Extract status
    if 'completed' in details_text.lower():
        transaction_data['status'] = 'Completed'
    elif 'pending' in details_text.lower():
        transaction_data['status'] = 'Pending'
    elif 'failed' in details_text.lower():
        transaction_data['status'] = 'Failed'
    
    # Store original texts
    transaction_data['raw_transaction'] = transaction_text
    transaction_data['raw_details'] = details_text
    
    return transaction_data

def parse_google_pay_activity(html_file):
    """
    Parse Google Pay activity from HTML file and save to CSV.
    
    Args:
        html_file (str): Path to the HTML file containing Google Pay activity
        
    Returns:
        pd.DataFrame: DataFrame containing the parsed transactions
    """
    try:
        if not os.path.exists(html_file):
            raise FileNotFoundError(f"HTML file not found: {html_file}")
        
        with open(html_file, 'r', encoding='utf-8') as file:
            content = file.read()
        
        head_end = content.find('</head>')
        if head_end == -1:
            raise ValueError("Could not find </head> tag in the HTML file")
        
        body_content = content[head_end + 7:]
        soup = BeautifulSoup(body_content, 'lxml')
        
        transactions = []
        transaction_divs = soup.find_all('div', class_='outer-cell mdl-cell mdl-cell--12-col mdl-shadow--2dp')
        
        if not transaction_divs:
            return pd.DataFrame()
        
        for transaction_div in transaction_divs:
            main_info = transaction_div.find('div', class_='content-cell mdl-cell mdl-cell--6-col mdl-typography--body-1')
            details = transaction_div.find('div', class_='content-cell mdl-cell mdl-cell--12-col mdl-typography--caption')
            
            if main_info and details:
                transaction_text = main_info.get_text(strip=True)
                details_text = details.get_text(strip=True)
                transaction_data = parse_transaction_details(transaction_text, details_text)
                transactions.append(transaction_data)
        
        if not transactions:
            return pd.DataFrame()
        
        df = pd.DataFrame(transactions)
        
        if 'date' in df.columns and not df['date'].isna().all():
            df = df.sort_values('date', ascending=False)
        
        output_file = 'google_pay_transactions.csv'
        df.to_csv(output_file, index=False, encoding='utf-8')
        
        return df
        
    except Exception:
        return pd.DataFrame()

if __name__ == "__main__":
    html_file = "My Activity.html"
    parse_google_pay_activity(html_file) 