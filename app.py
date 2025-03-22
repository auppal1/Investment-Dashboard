import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import requests
from prophet import Prophet


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


# AI prediction model using Facebook Prophet
# AI prediction model using Facebook Prophet
def predict_stock_prices(ticker):
    start_date = datetime.date.today() - datetime.timedelta(days=5 * 365)
    df = get_stock_data(ticker, start_date.strftime('%Y-%m-%d'))  # Fixed this line

    if df.empty:
        st.error("Not enough data to make prediction")
        return None

    # Convert to DataFrame and reset index
    df = df.reset_index()
    df = df[['Date', 'Close']].copy()

    # Rename columns as required by Prophet
    df = df.rename(columns={"Date": "ds", "Close": "y"})
    df['ds'] = pd.to_datetime(df['ds'])

    # Remove timezone if present
    df['ds'] = df['ds'].dt.tz_localize(None)  # Remove timezone from the 'ds' column

    # Initialize Prophet model
    model = Prophet(daily_seasonality=True)
    model.fit(df)

    # Make future predictions, no need to pass df again
    future = model.make_future_dataframe(df, periods=365)  # This line is now correct
    forecast = model.predict(future)

    today = datetime.date.today()
    target_dates = {
        "1 month": today + datetime.timedelta(days=30),
        "3 months": today + datetime.timedelta(days=90),
        "1 year": today + datetime.timedelta(days=365)
    }

    predictions = []
    for label, target_date in target_dates.items():
        target_ts = pd.Timestamp(target_date)
        forecast['diff'] = (forecast['ds'] - target_ts).abs()
        closest_row = forecast.loc[forecast['diff'].idxmin()]
        predicted_price = closest_row['yhat']
        predictions.append({
            "Timeframe": label,
            "Predicted Price": round(predicted_price, 2)
        })

    return predictions




# Function to calculate portfolio progression over time
# AI prediction model using Facebook Prophet
def predict_stock_prices(ticker):
    start_date = datetime.date.today() - datetime.timedelta(days=5 * 365)
    df = get_stock_data(ticker, start_date.strftime('%Y-%m-%d'))  # Fixed this line

    if df.empty:
        st.error("Not enough data to make prediction")
        return None

    # Convert to DataFrame and reset index
    df = df.reset_index()
    df = df[['Date', 'Close']].copy()

    # Rename columns as required by Prophet
    df = df.rename(columns={"Date": "ds", "Close": "y"})
    df['ds'] = pd.to_datetime(df['ds'])

    # Remove timezone if present
    df['ds'] = df['ds'].dt.tz_localize(None)  # Remove timezone from the 'ds' column

    # Initialize Prophet model
    model = Prophet(daily_seasonality=True)

    # Fit the model
    model.fit(df)

    # Generate future dataframe
    future = model.make_future_dataframe(df, periods=365, freq='D')  # Adding freq='D' ensures daily frequency

    # Perform prediction
    forecast = model.predict(future)

    today = datetime.date.today()
    target_dates = {
        "1 month": today + datetime.timedelta(days=30),
        "3 months": today + datetime.timedelta(days=90),
        "1 year": today + datetime.timedelta(days=365)
    }

    predictions = []
    for label, target_date in target_dates.items():
        target_ts = pd.Timestamp(target_date)
        forecast['diff'] = (forecast['ds'] - target_ts).abs()
        closest_row = forecast.loc[forecast['diff'].idxmin()]
        predicted_price = closest_row['yhat']
        predictions.append({
            "Timeframe": label,
            "Predicted Price": round(predicted_price, 2)
        })

    return predictions


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
    st.subheader("Portfolio Value Over Time")
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

st.subheader("AI-Powered Stock Price Predictions")

if st.button("Show AI Predictions"):
    with st.spinner("Predicting... Please wait."):
        predictions = predict_stock_prices(ticker)

        if predictions:
            st.table(pd.DataFrame(predictions))
