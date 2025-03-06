import requests
import logging
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# ----------------------------------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------------------------------

FMP_API_KEY = os.getenv("FMP_API_KEY")
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Initialize Groq Client
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# ----------------------------------------------------------------------------
# FETCH TOP GAINERS (FMP)
# ----------------------------------------------------------------------------


def fetch_top_gainers_from_fmp(limit: int = 10):
    """
    Fetch the top gainers from Financial Modeling Prep.
    """
    url = "https://financialmodelingprep.com/api/v3/stock_market/gainers"
    params = {"apikey": FMP_API_KEY}
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return [item.get("symbol", "Unknown") for item in data[:limit]]
    except requests.RequestException as e:
        logging.error(f"Error fetching top gainers from FMP: {e}")
        return []


# ----------------------------------------------------------------------------
# FETCH NEWS FOR SPECIFIC STOCK SYMBOLS (NEWSAPI)
# ----------------------------------------------------------------------------


def fetch_stock_news(ticker: str, limit: int = 5):
    """
    Fetch news related to a specific stock ticker from NewsAPI.
    """
    url = "https://newsapi.org/v2/everything"
    params = {
        "apiKey": NEWSAPI_KEY,
        "q": ticker,
        "language": "en",
        "pageSize": limit,
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return [
            {
                "title": art.get("title", "No title"),
                "url": art.get("url", ""),
                "source": art.get("source", {}).get("name", "Unknown"),
                "ticker": ticker,
            }
            for art in data.get("articles", [])
            if art.get("title")
        ]
    except requests.RequestException as e:
        logging.error(f"Error fetching news for {ticker}: {e}")
        return []


# ----------------------------------------------------------------------------
# SENTIMENT ANALYSIS WITH WEIGHTING (GROQ)
# ----------------------------------------------------------------------------


def analyze_sentiment_groq(text: str, source: str):
    """
    Perform sentiment analysis using Groq API and apply weighting.
    """
    if not client:
        logging.error(
            "GROQ_API_KEY is not set. Sentiment analysis cannot be performed."
        )
        return {"sentiment": "unknown", "confidence": 0.0}

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "Analyze the sentiment of the given text.",
                },
                {"role": "user", "content": text},
            ],
            model="llama-3.3-70b-versatile",
            stream=False,
        )
        sentiment = (
            chat_completion.choices[0].message.content
            if chat_completion.choices
            else "unknown"
        )
        confidence = 1.0  # Assuming a default confidence value

        # Weighting based on source credibility
        weight_factors = {
            "Bloomberg": 1.2,
            "Reuters": 1.1,
            "Yahoo Finance": 1.0,
            "Unknown": 0.8,
        }
        weight = weight_factors.get(source, 0.9)
        adjusted_confidence = round(confidence * weight, 2)

        return {
            "sentiment": sentiment,
            "confidence": adjusted_confidence,
        }
    except Exception as e:
        logging.error(f"Error calling Groq sentiment API: {e}")
        return {"sentiment": "unknown", "confidence": 0.0}


# ----------------------------------------------------------------------------
# ORCHESTRATION FUNCTION
# ----------------------------------------------------------------------------


def perform_market_research():
    """
    Fetch top gainers, fetch news for those stocks, analyze sentiment, and return results.
    """
    logging.info("Starting market research...")
    top_gainers = fetch_top_gainers_from_fmp(limit=10)

    all_news_articles = []
    for ticker in top_gainers:
        stock_news = fetch_stock_news(ticker, limit=3)  # Get news for each stock
        all_news_articles.extend(stock_news)

    analyzed_news = [
        {**article, **analyze_sentiment_groq(article["title"], article["source"])}
        for article in all_news_articles
    ]

    result = {"top_gainers": top_gainers, "analyzed_news": analyzed_news}
    logging.info("Market research completed.")
    return result


# ----------------------------------------------------------------------------
# DEMO USAGE
# ----------------------------------------------------------------------------
if __name__ == "__main__":
    final_data = perform_market_research()

    print("=== TOP GAINERS ===")
    for symbol in final_data["top_gainers"]:
        print(f" - {symbol}")

    print("\n=== NEWS & SENTIMENT ===")
    for item in final_data["analyzed_news"]:
        print(
            f"Ticker: {item['ticker']}\n"
            f"Title: {item['title']}\n"
            f"Source: {item['source']}\n"
            f"URL: {item['url']}\n"
            f"Sentiment: {item['sentiment']}, Confidence: {item['confidence']}\n"
            "---"
        )
