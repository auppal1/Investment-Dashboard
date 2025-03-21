import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import requests


# Cache function to fetch S&P 500 tickers from Wikipedia
@st.cache_data
def get_sp500_tickers():
    try:
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        html = requests.get(url).text
        df = pd.read_html(html)[0]
        return sorted(df['Symbol'].tolist())
    except Exception as e:
        st.error(f"Error fetching tickers: {e}")
        return []


# Set up the Streamlit page configuration
st.set_page_config(page_title='Investment Portfolio Dashboard', layout='wide')
st.title("Investment Portfolio Dashboard")

# Initialize session state for portfolio if not already present
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = []


# Function to fetch historical stock closing prices
def get_stock_data(ticker, start_date):
    stock = yf.Ticker(ticker)
    df = stock.history(start=start_date, end=datetime.date.today().strftime('%Y-%m-%d'))
    return df['Close'] if not df.empty else pd.Series()


# Function to fetch the latest available closing price for a stock
def get_latest_price(ticker):
    stock = yf.Ticker(ticker)
    df = stock.history(period='1d')
    return df['Close'].iloc[-1] if not df.empty else None


# Function to calculate portfolio progression over time
def calculate_portfolio_progression():
    distinct_holdings = {}

    # Combine duplicate tickers by summing shares and keeping the earliest purchase date
    for stock in st.session_state.portfolio:
        ticker, shares, purchase_date = stock['ticker'], stock['shares'], stock['date']
        if ticker in distinct_holdings:
            distinct_holdings[ticker]['shares'] += shares
            distinct_holdings[ticker]['date'] = min(distinct_holdings[ticker]['date'], purchase_date)
        else:
            distinct_holdings[ticker] = {'shares': shares, 'date': purchase_date}

    portfolio_value_df = None

    # Fetch historical stock prices and compute daily portfolio value
    for ticker, holding in distinct_holdings.items():
        prices = get_stock_data(ticker, holding['date'])
        if not prices.empty:
            stock_value_df = (prices * holding['shares']).to_frame(ticker)
            portfolio_value_df = stock_value_df if portfolio_value_df is None else portfolio_value_df.join(
                stock_value_df, how='outer')

    if portfolio_value_df is not None:
        portfolio_value_df = portfolio_value_df.sort_index().fillna(method='ffill').fillna(0)
        portfolio_value_df['Total Value'] = portfolio_value_df.sum(axis=1)
        portfolio_value_df = portfolio_value_df.reset_index().rename(columns={'index': 'Date'})
        return portfolio_value_df

    return pd.DataFrame()


# Fetch S&P 500 tickers
sp500_tickers = get_sp500_tickers()


# Autocomplete search for stock ticker selection
def autocomplete_search():
    return st.selectbox("Select Ticker", sorted(sp500_tickers))


ticker = autocomplete_search()
shares = st.number_input("Number of Shares", min_value=1, step=1)
date = st.date_input("Purchase Date", min_value=datetime.date(2000, 1, 1), max_value=datetime.date.today())

# Button to add stock to portfolio
if st.button("Add to Portfolio") and ticker:
    st.session_state.portfolio.append({'ticker': ticker, 'shares': shares, 'date': str(date)})
    st.rerun()

# Display portfolio progression chart if portfolio exists
if st.session_state.portfolio:
    progression_df = calculate_portfolio_progression()
    if not progression_df.empty:
        fig, ax = plt.subplots()
        ax.plot(progression_df['Date'], progression_df['Total Value'], label='Total Portfolio Value', color='blue')
        ax.set_title("Portfolio Value Over Time")
        ax.set_xlabel("Date")
        ax.set_ylabel("Portfolio Value")
        ax.legend()
        st.pyplot(fig)
    else:
        st.info("No data available to plot portfolio progression.")

# Display portfolio holdings
if st.session_state.portfolio:
    holdings = {}

    # Aggregate holdings by ticker
    for entry in st.session_state.portfolio:
        ticker = entry['ticker']
        holdings[ticker] = holdings.get(ticker, 0) + entry['shares']

    aggregated_holdings = []
    for ticker, total_shares in holdings.items():
        latest_price = get_latest_price(ticker)
        if latest_price is not None:
            aggregated_holdings.append({
                'Ticker': ticker,
                'Shares': total_shares,
                'Current Value': round(total_shares * latest_price, 2)
            })

    if aggregated_holdings:
        st.subheader("Portfolio Holdings")
        holdings_df = pd.DataFrame(aggregated_holdings)
        st.dataframe(holdings_df)
    else:
        st.info("No holdings to display yet.")