import requests
from typing import List, Dict
from groq import Groq

# API Keys (Replace with your actual keys)
NEWSAPI_KEY = "5708ae6f4c0f45b3adfedc0d387dab5c"
GROQ_API_KEY = "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"

# Initialize Groq Client
groq_client = Groq(api_key=GROQ_API_KEY)


# 1. Fetch News Data from NewsAPI
def get_newsapi_articles(ticker: str) -> List[Dict]:
    url = (
        f"https://newsapi.org/v2/everything?q={ticker}&sortBy=publishedAt"
        f"&apiKey={NEWSAPI_KEY}"
    )
    response = requests.get(url).json()
    return response.get("articles", [])[:10]  # Fetch up to 10 latest news articles


def analyze_sentiment(news_articles: List[Dict]) -> Dict[str, float]:
    """Analyzes sentiment of news headlines using Groq and provides an aggregated sentiment score."""
    if not news_articles:
        return {"positive": 0, "negative": 0, "neutral": 1}

    headlines = "\n".join([article["title"] for article in news_articles])
    prompt = (
        "Analyze the sentiment of the following financial news headlines. "
        "Provide percentages for positive, negative, and neutral sentiments:\n\n"
        f"{headlines}\n\n"
        "Respond strictly in JSON format like:\n"
        '{"positive": 0.7, "negative": 0.2, "neutral": 0.1}'
    )

    completion = groq_client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}], model="llama3-8b-8192"
    )

    sentiment_json = completion.choices[0].message.content.strip()
    try:
        sentiment = eval(sentiment_json)  # Convert JSON response into dict
        return sentiment
    except:
        return {"positive": 0, "negative": 0, "neutral": 1}


# Example Testing of the Sentiment Analysis Tool
if __name__ == "__main__":
    ticker = "AAPL"

    print("\n--- Fetching News from NewsAPI ---")
    newsapi_articles = get_newsapi_articles(ticker)
    print(newsapi_articles)

    print("\n--- Performing Sentiment Analysis on NewsAPI Articles ---")
    newsapi_sentiment = analyze_sentiment(newsapi_articles)
    print(newsapi_sentiment)
