import os
import logging
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import csv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_google_pay_activity(html_file):
    """
    Parse Google Pay activity from HTML file and save to CSV.
    
    Args:
        html_file (str): Path to the HTML file containing Google Pay activity
        
    Returns:
        pd.DataFrame: DataFrame containing the parsed transactions
    """
    try:
        # Check if file exists
        if not os.path.exists(html_file):
            raise FileNotFoundError(f"HTML file not found: {html_file}")
            
        logger.info(f"Reading HTML file: {html_file}")
        with open(html_file, 'r', encoding='utf-8') as file:
            html_content = file.read()
            
        # Find the content after </head>
        head_end = html_content.find('</head>')
        if head_end == -1:
            raise ValueError("Could not find </head> tag in the HTML file")
            
        body_content = html_content[head_end + 7:]  # 7 is the length of </head>
        
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(body_content, 'html.parser')
        
        # Extract transaction details
        transactions = []
        transaction_divs = soup.find_all('div', class_='outer-cell mdl-cell mdl-cell--12-col mdl-shadow--2dp')
        
        if not transaction_divs:
            logger.warning("No transaction entries found in the HTML file")
            return pd.DataFrame()
            
        logger.info(f"Found {len(transaction_divs)} transaction entries")
        
        for transaction_div in transaction_divs:
            main_info = transaction_div.find('div', class_='content-cell mdl-cell mdl-cell--6-col mdl-typography--body-1')
            details = transaction_div.find('div', class_='content-cell mdl-cell mdl-cell--12-col mdl-typography--caption')
            
            if main_info and details:
                transaction_text = main_info.get_text(strip=True)
                details_text = details.get_text(strip=True)
                transactions.append({
                    'transaction': transaction_text,
                    'details': details_text
                })
            else:
                logger.warning("Skipping transaction due to missing main info or details")
        
        if not transactions:
            logger.warning("No valid transactions were extracted")
            return pd.DataFrame()
            
        # Save the extracted data to a CSV file
        output_file = 'google_pay_transactions.csv'
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['transaction', 'details']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for transaction in transactions:
                    writer.writerow(transaction)
            logger.info(f"Successfully saved {len(transactions)} transactions to {output_file}")
        except IOError as e:
            logger.error(f"Error writing to CSV file: {e}")
            raise
            
        return pd.DataFrame(transactions)
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        html_file = "My Activity.html"
        df = parse_google_pay_activity(html_file)
        if not df.empty:
            print(f"\nSuccessfully processed {len(df)} transactions")
        else:
            print("\nNo transactions were processed")
    except Exception as e:
        print(f"\nError: {str(e)}")
        exit(1) 