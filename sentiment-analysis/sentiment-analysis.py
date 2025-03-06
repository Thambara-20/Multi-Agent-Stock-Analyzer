import requests
import logging
import os
from typing import List, Dict, Optional
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# API Keys
FMP_API_KEY = os.getenv("FMP_API_KEY", "your_fmp_api_key")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "your_alpha_vantage_api_key")
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY", "your_polygon_api_key")


class DataCollector:
    def __init__(self):
        self.base_urls = {
            "fmp": "https://financialmodelingprep.com/api/v3",
            "alpha": "https://www.alphavantage.co/query",
            "polygon": "https://api.polygon.io/v2",
        }
        self.api_keys = {
            "fmp": FMP_API_KEY,
            "alpha": ALPHA_VANTAGE_API_KEY,
            "polygon": POLYGON_API_KEY,
        }

    def fetch_data(
        self, source: str, endpoint: str, params: Optional[Dict] = None
    ) -> Optional[Dict]:
        """Generic method to fetch data from different APIs."""
        try:
            if source not in self.base_urls:
                logging.error(f"Unknown API source: {source}")
                return None

            url = f"{self.base_urls[source]}{endpoint}"
            params = params or {}
            if source in self.api_keys:
                params["apiKey"] = self.api_keys[source]

            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logging.error(f"HTTP Request Error fetching {endpoint} from {source}: {e}")
            return None

    def fetch_polygon_aggregates(self, ticker: str, date: str) -> Optional[Dict]:
        """Fetch aggregated market data from Polygon.io for a given ticker and date."""
        try:
            url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{date}/{date}"
            params = {"apiKey": self.api_keys["polygon"]}
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logging.error(
                f"HTTP Request Error fetching aggregate data for {ticker} on {date}: {e}"
            )
            return None


class GetNews:
    """Class to fetch news from different sources without requiring an API key."""

    @staticmethod
    def fetch_reuters_news() -> List[Dict]:
        """Fetch latest financial news from Reuters (without API key)."""
        try:
            url = "https://www.reuters.com/markets"
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            headlines = soup.find_all("h3", class_="story-title")
            return [
                {"source": "Reuters", "title": h.text.strip(), "url": url}
                for h in headlines[:5]
            ]
        except requests.RequestException as e:
            logging.error(f"Error fetching Reuters news: {e}")
            return []

    @staticmethod
    def fetch_bbc_news() -> List[Dict]:
        """Fetch latest financial news from BBC (without API key)."""
        try:
            url = "https://www.bbc.com/news/business"
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            headlines = soup.find_all("h3")
            return [
                {"source": "BBC", "title": h.text.strip(), "url": url}
                for h in headlines[:5]
            ]
        except requests.RequestException as e:
            logging.error(f"Error fetching BBC news: {e}")
            return []

    @staticmethod
    def fetch_yahoo_finance_news() -> List[Dict]:
        """Fetch latest financial news from Yahoo Finance (without API key)."""
        try:
            url = "https://finance.yahoo.com/news"
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            headlines = soup.find_all("h3")
            return [
                {"source": "Yahoo Finance", "title": h.text.strip(), "url": url}
                for h in headlines[:5]
            ]
        except requests.RequestException as e:
            logging.error(f"Error fetching Yahoo Finance news: {e}")
            return []

    @staticmethod
    def fetch_marketwatch_news() -> List[Dict]:
        """Fetch latest financial news from MarketWatch (without API key)."""
        try:
            url = "https://www.marketwatch.com/latest-news"
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            headlines = soup.find_all("h3")
            return [
                {"source": "MarketWatch", "title": h.text.strip(), "url": url}
                for h in headlines[:5]
            ]
        except requests.RequestException as e:
            logging.error(f"Error fetching MarketWatch news: {e}")
            return []


# Fetch news articles from multiple sources
def get_free_news_articles() -> List[Dict]:
    """Fetches recent and relevant news articles from various sources."""
    collector = DataCollector()
    try:
        polygon_news = collector.fetch_data("polygon", "/reference/news", {"limit": 10})
        articles = (
            [
                {
                    "source": article.get("publisher", {}).get("name", "Unknown"),
                    "title": article.get("title", "No Title"),
                    "url": article.get("article_url", "No URL"),
                    "publishedAt": article.get("published_utc", "Unknown"),
                }
                for article in polygon_news.get("results", [])[:10]
            ]
            if polygon_news
            else []
        )

        # Fetch non-API news
        articles.extend(GetNews.fetch_reuters_news())
        articles.extend(GetNews.fetch_bbc_news())
        articles.extend(GetNews.fetch_yahoo_finance_news())
        articles.extend(GetNews.fetch_marketwatch_news())

        logging.info(f"Fetched {len(articles)} latest news articles")
        return articles
    except Exception as e:
        logging.error(f"Unexpected Error fetching news articles: {e}")
        return []


# Example Testing of the Data Collection Tool
if __name__ == "__main__":
    logging.info("Starting news collection...")
    latest_news = get_free_news_articles()
    logging.info(f"Final collected news data: {latest_news}")
