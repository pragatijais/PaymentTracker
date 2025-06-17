import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Read the transactions CSV
transactions = pd.read_csv('google_pay_transactions.csv', encoding='utf-8')

# Ensure amount is numeric
transactions['amount'] = pd.to_numeric(transactions['amount'], errors='coerce').fillna(0)

# Parse date and extract day of week and time of day
transactions['datetime'] = pd.to_datetime(transactions['date'], errors='coerce')
transactions['date_only'] = transactions['datetime'].dt.date
transactions['day_of_week'] = transactions['datetime'].dt.day_name()
transactions['hour'] = transactions['datetime'].dt.hour

def get_time_of_day(hour):
    if pd.isnull(hour):
        return 'Unknown'
    if 5 <= hour < 12:
        return 'Morning'
    elif 12 <= hour < 17:
        return 'Afternoon'
    elif 17 <= hour < 21:
        return 'Evening'
    else:
        return 'Night'

transactions['time_of_day'] = transactions['hour'].apply(get_time_of_day)

# If no category column, create a simple one based on recipient
if 'category' not in transactions.columns:
    def categorize(recipient):
        recipient = str(recipient).lower()
        if any(x in recipient for x in ['food', 'restaurant', 'cafe', 'hotel', 'dining', 'eats', 'swiggy', 'zomato']):
            return 'Food & Dining'
        elif any(x in recipient for x in ['shop', 'store', 'market', 'mart', 'flipkart', 'amazon', 'myntra']):
            return 'Shopping'
        elif any(x in recipient for x in ['transport', 'uber', 'ola', 'metro', 'bus', 'train', 'taxi', 'auto']):
            return 'Transportation'
        elif any(x in recipient for x in ['salon', 'spa', 'beauty', 'gym', 'fitness']):
            return 'Personal Care'
        else:
            return 'Others'
    transactions['category'] = transactions['recipient'].apply(categorize)

# Set up the plot
sns.set_theme(style="whitegrid")
fig = plt.figure(figsize=(20, 15))
gs = fig.add_gridspec(3, 2)

# 1. Spending by Category (Pie Chart)
ax1 = fig.add_subplot(gs[0, 0])
category_totals = transactions.groupby('category')['amount'].sum()
ax1.pie(category_totals, labels=category_totals.index, autopct='%1.1f%%')
ax1.set_title('Spending Distribution by Category')

# 2. Daily Spending Trend (Line Plot)
ax2 = fig.add_subplot(gs[0, 1])
daily_spending = transactions.groupby('date_only')['amount'].sum().reset_index()
sns.lineplot(data=daily_spending, x='date_only', y='amount', ax=ax2)
ax2.set_title('Daily Spending Trend')
ax2.tick_params(axis='x', rotation=45)

# 3. Spending by Day of Week (Bar Plot)
ax3 = fig.add_subplot(gs[1, 0])
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
sns.barplot(data=transactions, x='day_of_week', y='amount', order=day_order, ax=ax3)
ax3.set_title('Spending by Day of Week')
ax3.tick_params(axis='x', rotation=45)

# 4. Spending by Time of Day (Bar Plot)
ax4 = fig.add_subplot(gs[1, 1])
time_order = ['Morning', 'Afternoon', 'Evening', 'Night']
sns.barplot(data=transactions, x='time_of_day', y='amount', order=time_order, ax=ax4)
ax4.set_title('Spending by Time of Day')

# 5. Transaction Amount Distribution (Histogram)
ax5 = fig.add_subplot(gs[2, 0])
sns.histplot(data=transactions, x='amount', bins=30, ax=ax5)
ax5.set_title('Transaction Amount Distribution')

# 6. Top Recipients (Bar Plot)
ax6 = fig.add_subplot(gs[2, 1])
top_recipients = transactions.groupby('recipient')['amount'].sum().nlargest(10)
sns.barplot(x=top_recipients.values, y=top_recipients.index, ax=ax6)
ax6.set_title('Top 10 Recipients by Amount')

plt.tight_layout()
plt.savefig('transaction_analysis.png', dpi=300, bbox_inches='tight')
plt.close() 