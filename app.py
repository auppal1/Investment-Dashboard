import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import requests


@st.cache_data
def get_sp500_tickers():
    try:
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        html = requests.get(url).text
        df = pd.read_html(html)[0]
        tickers = df['Symbol'].tolist()
        return sorted(tickers)
    except Exception as e:
        st.error(f"Error fetching tickers: {e}")
        return []


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
sp500_tickers = get_sp500_tickers()

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


# # ticker = st.text_input("Stock Ticker (e.g., AAPL, TSLA)").upper()
# shares = st.number_input("Number of Shares", min_value=1, step=1)
# date = st.date_input("Purchase Date", min_value=datetime.date(2000, 1, 1), max_value=datetime.date.today())
#
# if st.button("Add to Portfolio") and ticker:
#     st.session_state.portfolio.append({'ticker': ticker, 'shares': shares, 'date': str(date)})
#     st.rerun()

def autocomplete_search():
    # ticker = st.text_input("Stock ticker", key="ticker_input")
    #
    # filtered_tickers = []
    #
    # if ticker:
    #     filtered_tickers = [t for t in sp500_tickers if ticker.upper() in t.upper()]
    #
    # if filtered_tickers:
    #     st.write("Suggestions: ")
    #     for suggested_ticker in filtered_tickers[:5]:
    #         if st.button(suggested_ticker, key=f"suggest_{suggested_ticker}"):
    #             st.session_state.ticker_input = suggested_ticker
    #
    # return ticker
    # user_input = st.text_input("Enter stock ticker: ", key="ticker_input")
    # if sp500_tickers:
    #     if user_input:
    #         matching_tickers = [ticker for ticker in sp500_tickers if user_input.upper() in ticker.upper()]
    #     else:
    #         matching_tickers = sp500_tickers
    #     if matching_tickers:
    #         selected_ticker = st.selectbox("Select ticker", sorted(matching_tickers), key="ticker_select")
    #     else:
    #         st.warning("No matching tickers found. Please refine your input.")
    #         selected_ticker = user_input.upper()
    #
    # else:
    #     st.error("No tickers available")
    #     selected_ticker = user_input.upper()
    selected_ticker = st.selectbox("Selected ticker ", sorted(sp500_tickers))
    return selected_ticker


ticker = autocomplete_search()

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
