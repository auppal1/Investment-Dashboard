import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import datetime

# Set up the page
st.set_page_config(page_title='Investment Portfolio Dashboard', layout='wide')
st.title("Investment Portfolio Dashboard")

# Initialize session state if not present
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = []


# Function to fetch stock data
def get_stock_data(ticker, start_date):
    stock = yf.Ticker(ticker)
    df = stock.history(start=start_date, end=datetime.date.today().strftime('%Y-%m-%d'))
    return df['Close']


# Function to calculate portfolio value
def calculate_portfolio_value():
    portfolio_values = []
    dates = []
    for stock in st.session_state.portfolio:
        prices = get_stock_data(stock['ticker'], stock['date'])
        if len(prices) > 0:
            purchase_price = prices.iloc[0]  # Get the price on the purchase date
            values = purchase_price * stock['shares']
            if len(dates) == 0:
                dates = prices.index
            portfolio_values.append(values)

    if portfolio_values:
        total_portfolio_value = sum(portfolio_values)
        return pd.DataFrame({'Date': dates, 'Portfolio Value': total_portfolio_value})
    return pd.DataFrame()


# Fetch S&P 500 data
sp500_data = get_stock_data('^GSPC', '2023-01-01')

# Portfolio growth comparison
portfolio_df = calculate_portfolio_value()
if not portfolio_df.empty:
    fig, ax = plt.subplots()
    ax.plot(portfolio_df['Date'], portfolio_df['Portfolio Value'], label='Portfolio Value')
    ax.plot(sp500_data.index, sp500_data, label='S&P 500', linestyle='dashed')
    ax.set_title("Portfolio Growth vs. S&P 500")
    ax.set_xlabel("Date")
    ax.set_ylabel("Value")
    ax.legend()
    st.pyplot(fig)

# User input for stocks
st.subheader("Add a Stock to Your Portfolio")
ticker = st.text_input("Stock Ticker (e.g., AAPL, TSLA)").upper()
shares = st.number_input("Number of Shares", min_value=1, step=1)
date = st.date_input("Purchase Date", min_value=datetime.date(2000, 1, 1), max_value=datetime.date.today())

if st.button("Add to Portfolio") and ticker:
    st.session_state.portfolio.append({'ticker': ticker, 'shares': shares, 'date': str(date)})
    st.rerun()

# Display portfolio allocation
if st.session_state.portfolio:
    portfolio_data = []
    for stock in st.session_state.portfolio:
        prices = get_stock_data(stock['ticker'], stock['date'])
        if len(prices) > 0:
            purchase_price = prices.iloc[0]
            total_value = stock['shares'] * purchase_price
            portfolio_data.append({'ticker': stock['ticker'], 'Total Value': total_value})

    if portfolio_data:
        portfolio_df = pd.DataFrame(portfolio_data)
        fig, ax = plt.subplots()
        ax.pie(portfolio_df['Total Value'], labels=portfolio_df['ticker'], autopct='%1.1f%%', startangle=90)
        ax.set_title("Portfolio Allocation")
        st.pyplot(fig)
