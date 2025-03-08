import numpy as np
import pandas as pd
from fundamental.fundamental_tools import get_fundamental_analysis
from fundamental.weight import generate_weight_metrics

# Generate dynamic weights using LLM
WEIGHTS = generate_weight_metrics()

# If LLM fails, use fallback weights
if not WEIGHTS:
    WEIGHTS = {
        "EPS": 0.15,
        "PE_Ratio": -0.05,  # Lower is better, so negative weight
        "PB_Ratio": -0.05,  # Lower is better
        "PEG_Ratio": -0.05,  # Lower is better
        "Total_Revenue": 0.10,
        "Revenue_Growth": 0.15,
        "EPS_Growth_YoY": 0.10,
        "Net_Profit_Margin": 0.10,
        "Operating_Margin": 0.10,
        "ROE": 0.10,
        "ROA": 0.10,
        "Debt_to_Equity": -0.05,  # Lower is better
        "Operating_Cash_Flow": 0.10,
        "Free_Cash_Flow": 0.10,
        "Dividend_Yield": 0.05,
        "Payout_Ratio": -0.05  # Lower is better
    }


def normalize(value, min_val, max_val):
    """Normalize a value to the range [0, 1] using Min-Max Scaling."""
    if min_val == max_val:  # Avoid division by zero
        return 0.5  # Neutral value
    return (value - min_val) / (max_val - min_val)


def rank_companies(ticker_list):
    """
    Fetch fundamental data for multiple companies, calculate weighted scores, and rank them.
    :param ticker_list: List of company tickers to evaluate.
    :return: DataFrame with ranked companies.
    """
    company_scores = []
    # return

    # Fetch fundamental data for all companies
    company_data = []
    for ticker in ticker_list:
        data = get_fundamental_analysis.invoke(ticker)
        if data:
            data["Ticker"] = ticker
            company_data.append(data)

    # Convert to DataFrame
    df = pd.DataFrame(company_data)

    # Ensure all required columns exist
    for key in WEIGHTS.keys():
        if key not in df.columns:
            df[key] = None  # Fill missing columns

    # ✅ FIX: Fill missing values and manually convert only numeric columns
    df.fillna(0, inplace=True)

    # Convert only numeric columns to float, keeping "Ticker" as string
    numeric_cols = [col for col in df.columns if col not in ["Ticker"]]
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')

    # Normalize each metric
    for metric in WEIGHTS.keys():
        min_val, max_val = df[metric].min(), df[metric].max()
        df[metric] = df[metric].apply(lambda x: normalize(x, min_val, max_val))

    # Calculate weighted scores
    df["Final_Score"] = df[numeric_cols].mul(pd.Series(WEIGHTS)).sum(axis=1)

    # Rank companies
    df.sort_values(by="Final_Score", ascending=False, inplace=True)

    # Display the top 5 companies
    print("📊 Top 5 Ranked Companies:")
    print(df[["Ticker", "Final_Score"]].head(10))

    return df[["Ticker", "Final_Score"]].head(10)

