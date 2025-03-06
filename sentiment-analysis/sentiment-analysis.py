import requests
import logging
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# API Keys (Replace with your actual keys)
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

# //load dot Env


# Fetch trending stocks for the day
def get_top_stocks_alpha_vantage() -> List[str]:
    """Fetches the top trending investable stocks in the US market for the current day."""
    try:
        url = f"https://www.alphavantage.co/query?function=TOP_GAINERS_LOSERS&apikey={ALPHA_VANTAGE_API_KEY}"
        response = requests.get(url).json()
        top_gainers = response.get("top_gainers", [])[:5]  # Limit to top 5 gainers
        logging.info(f"Fetched top gainers: {top_gainers}")
        return [stock["ticker"] for stock in top_gainers]
    except Exception as e:
        logging.error(f"Error fetching top stocks: {e}")
        return []


def get_top_gainers_financial_modeling() -> List[Dict]:
    """Fetches the top gaining stocks in the US market for the current day."""
    try:
        url = "https://financialmodelingprep.com/api/v3/stock_market/gainers"
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        top_gainers = response.json()[:5]  # Limit to top 5 gainers
        logging.info(f"Fetched top gainers: {top_gainers}")
        return top_gainers
    except requests.RequestException as e:
        logging.error(f"Error fetching top gainers: {e}")
        return []


# Fetch news articles related to a given stock
def get_newsapi_articles(ticker: str) -> List[Dict]:
    """Fetches recent and relevant news articles about a given stock ticker."""
    try:
        url = (
            f"https://newsapi.org/v2/everything?q={ticker}&sortBy=publishedAt"
            f"&apiKey={NEWSAPI_KEY}"
        )
        response = requests.get(url).json()
        logging.info(f"Fetched news for {ticker}: {response}")
        articles = [
            {
                "source": article["source"]["name"],
                "title": article["title"],
                "url": article["url"],
                "publishedAt": article["publishedAt"],
            }
            for article in response.get("articles", [])[:5]
        ]  # Fetch top 5 articles
        logging.info(f"Fetched {len(articles)} articles for {ticker}")
        return articles
    except Exception as e:
        logging.error(f"Error fetching news for {ticker}: {e}")
        return []


# Fetch sentiment-related data from Finnhub
def get_finnhub_sentiment(ticker: str) -> Dict:
    """Fetches sentiment-related financial news data from Finnhub."""
    try:
        url = f"https://finnhub.io/api/v1/news-sentiment?symbol={ticker}&token={FINNHUB_API_KEY}"
        response = requests.get(url).json()
        sentiment_data = {
            "sentiment_score": response.get("companyNewsScore", 0),
            "news_count": response.get("newsScore", 0),
            "positive": response.get("positiveScore", 0),
            "negative": response.get("negativeScore", 0),
        }
        logging.info(f"Fetched sentiment data for {ticker}: {sentiment_data}")
        return sentiment_data
    except Exception as e:
        logging.error(f"Error fetching sentiment data for {ticker}: {e}")
        return {}


# Structure the collected data
def collect_market_data() -> List[Dict]:
    """Collects and structures data for the top trending stocks."""
    try:
        top_stocks_alpha_vantage = get_top_stocks_alpha_vantage()
        # top_gainers_financial_modeling = get_top_gainers_financial_modeling()

        structured_data = []

        for stock in top_stocks_alpha_vantage:
            news_articles = get_newsapi_articles(stock)
            sentiment_data = get_finnhub_sentiment(stock)
            structured_data.append(
                {
                    "ticker": stock,
                    "news": news_articles,
                    "sentiment_data": sentiment_data,
                }
            )

        logging.info(f"Collected market data for {len(top_stocks)} stocks.")
        return structured_data
    except Exception as e:
        logging.error(f"Error collecting market data: {e}")
        return []


# Example Testing of the Data Collection Tool
if __name__ == "__main__":
    logging.info("Starting data collection for top investable stocks...")
    market_data = collect_market_data()
    logging.info(f"Final structured market data: {market_data}")
