import time
from langchain_core.tools import tool
import yfinance as yf
from functools import lru_cache

# Dictionary to cache stock data to avoid multiple API calls
stock_data_cache = {}


def fetch_stock_data(ticker: str, start_date: str, end_date: str, interval: str = "1d", cache_duration=3600):
    """
    Fetch stock data only once per ticker for the given time period.
    Cache expires after `cache_duration` seconds.
    """
    cache_key = f"{ticker}_{start_date}_{end_date}_{interval}"
    current_time = time.time()

    # Check if data exists and is still valid
    if cache_key in stock_data_cache:
        cached_time, data = stock_data_cache[cache_key]
        if current_time - cached_time < cache_duration:
            return data  # Use cached data

    # Fetch new data and update cache
    stock = yf.Ticker(ticker)
    data = stock.history(start=start_date, end=end_date, interval=interval)
    stock_data_cache[cache_key] = (current_time, data)
    
    return data



@tool
def get_historical_prices(ticker: str, start_date: str, end_date: str, interval: str = "1d"):
    """
    Fetch historical OHLC price data for a given stock.
    """
    data = fetch_stock_data(ticker, start_date, end_date, interval)
    return data.reset_index().to_dict(orient="records")


@tool
def get_volume_data(ticker: str, start_date: str, end_date: str, interval: str = "1d"):
    """
    Fetch trading volume data for a given stock.
    """
    data = fetch_stock_data(ticker, start_date, end_date, interval)
    return data[["Volume"]].reset_index().to_dict(orient="records")


@tool
def calculate_technical_indicators(ticker: str, start_date: str, end_date: str):
    """
    Calculate technical indicators for a stock.
    """
    data = fetch_stock_data(ticker, start_date, end_date)

    # Moving Averages
    data["MA_50"] = data["Close"].rolling(window=50).mean()
    data["MA_200"] = data["Close"].rolling(window=200).mean()

    # RSI Calculation
    delta = data["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data["RSI"] = 100 - (100 / (1 + rs))

    # MACD Calculation
    short_ema = data["Close"].ewm(span=12, adjust=False).mean()
    long_ema = data["Close"].ewm(span=26, adjust=False).mean()
    data["MACD"] = short_ema - long_ema
    data["Signal_Line"] = data["MACD"].ewm(span=9, adjust=False).mean()

    # Bollinger Bands
    data["BB_Middle"] = data["Close"].rolling(window=20).mean()
    data["BB_Upper"] = data["BB_Middle"] + (data["Close"].rolling(window=20).std() * 2)
    data["BB_Lower"] = data["BB_Middle"] - (data["Close"].rolling(window=20).std() * 2)

    # Stochastic Oscillator
    data["L14"] = data["Low"].rolling(window=14).min()
    data["H14"] = data["High"].rolling(window=14).max()
    data["%K"] = (data["Close"] - data["L14"]) / (data["H14"] - data["L14"]) * 100
    data["%D"] = data["%K"].rolling(window=3).mean()

    return data.reset_index().to_dict(orient="records")


@tool
def get_intraday_data(ticker: str, start_date: str, end_date: str, interval: str = "5m"):
    """
    Fetch intraday price and volume data.
    """
    data = fetch_stock_data(ticker, start_date, end_date, interval)
    return data.reset_index().to_dict(orient="records")


parmas = {
    "ticker": "AAPL",
    "start_date": "2020-01-01",
    "end_date": "2021-01-01"
}

print(get_intraday_data(parmas))