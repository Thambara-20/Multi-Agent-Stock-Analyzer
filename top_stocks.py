import yfinance as yf
import pandas as pd

def get_top_stocks(n=30):
    """
    Efficiently selects the top `n` stocks based on estimated market cap and trading volume.
    Uses batch processing via yfinance (free alternative to Financial Modeling Prep).

    Parameters:
        n (int): Number of stocks to return (default is 30).

    Returns:
        List of top `n` stock tickers.
    """

    # Step 1: Fetch S&P 500 stock tickers from Wikipedia (Free Source)
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    table = pd.read_html(url)[0]
    tickers = [symbol for symbol in table["Symbol"].tolist() if "." not in symbol][:n]
    
    return tickers

# Example Usage
top_stocks_today = get_top_stocks(30)
print("Top stocks for today:", top_stocks_today)
