import os
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import csv

def parse_google_pay_activity(html_file):
    # Read the HTML file
    with open(html_file, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Find the end of the head section
    head_end = content.find('</head>')
    if head_end == -1:
        raise ValueError("Could not find </head> tag in the HTML file")
    
    # Get the content after </head>
    body_content = content[head_end + 7:]  # 7 is the length of '</head>'
    
    # Parse the HTML content
    soup = BeautifulSoup(body_content, 'html.parser')
    
    # Extract transaction details
    transactions = []
    for transaction_div in soup.find_all('div', class_='outer-cell mdl-cell mdl-cell--12-col mdl-shadow--2dp'):
        main_info = transaction_div.find('div', class_='content-cell mdl-cell mdl-cell--6-col mdl-typography--body-1')
        details = transaction_div.find('div', class_='content-cell mdl-cell mdl-cell--12-col mdl-typography--caption')
        
        if main_info and details:
            transaction_text = main_info.get_text(strip=True)
            details_text = details.get_text(strip=True)
            transactions.append({
                'transaction': transaction_text,
                'details': details_text
            })

    # Save the extracted data to a CSV file
    with open('google_pay_transactions.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['transaction', 'details']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for transaction in transactions:
            writer.writerow(transaction)

    print("Data has been successfully extracted and saved to 'google_pay_transactions.csv'.")
    
    return pd.DataFrame(transactions)

if __name__ == "__main__":
    html_file = "My Activity.html"
    if os.path.exists(html_file):
        try:
            df = parse_google_pay_activity(html_file)
            print("\nFirst few transactions:")
            print(df.head())
        except Exception as e:
            print(f"Error processing file: {e}")
    else:
        print(f"File {html_file} not found") 