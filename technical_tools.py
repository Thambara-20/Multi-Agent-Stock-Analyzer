from langchain.tools import tool
import yfinance as yf

@tool
def get_historical_prices(ticker: str, start_date: str, end_date: str, interval: str = "1d"):
    """
    Fetch historical OHLC price data for a given stock.
    :param ticker: Stock symbol (e.g., 'AAPL').
    :param start_date: Start date (YYYY-MM-DD).
    :param end_date: End date (YYYY-MM-DD).
    :param interval: Data interval ('1d', '1h', '5m', etc.).
    :return: DataFrame with historical prices.
    """
    stock = yf.Ticker(ticker)
    data = stock.history(start=start_date, end=end_date, interval=interval)
    return data.reset_index().to_dict(orient="records")


@tool
def get_volume_data(ticker: str, start_date: str, end_date: str, interval: str = "1d"):
    """
    Fetch trading volume data for a given stock.
    :param ticker: Stock symbol (e.g., 'AAPL').
    :param start_date: Start date (YYYY-MM-DD).
    :param end_date: End date (YYYY-MM-DD).
    :param interval: Data interval ('1d', '1h', '5m', etc.).
    :return: DataFrame with volume data.
    """
    stock = yf.Ticker(ticker)
    data = stock.history(start=start_date, end=end_date, interval=interval)
    return data[["Date", "Volume"]].reset_index().to_dict(orient="records")


import pandas as pd
import numpy as np

@tool
def calculate_technical_indicators(ticker: str, start_date: str, end_date: str):
    """
    Calculate technical indicators for a stock.
    :param ticker: Stock symbol (e.g., 'AAPL').
    :param start_date: Start date (YYYY-MM-DD).
    :param end_date: End date (YYYY-MM-DD).
    :return: Dictionary with calculated indicators.
    """
    stock = yf.Ticker(ticker)
    data = stock.history(start=start_date, end=end_date)

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
    :param ticker: Stock symbol (e.g., 'AAPL').
    :param start_date: Start date (YYYY-MM-DD).
    :param end_date: End date (YYYY-MM-DD).
    :param interval: Intraday interval ('1m', '5m', '15m', '1h').
    :return: DataFrame with intraday price and volume.
    """
    stock = yf.Ticker(ticker)
    data = stock.history(start=start_date, end=end_date, interval=interval)
    return data.reset_index().to_dict(orient="records")
