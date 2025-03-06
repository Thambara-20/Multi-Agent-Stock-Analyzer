import os
import requests
from dotenv import load_dotenv
from langchain_core.tools import tool
import yfinance as yf
import langgraph.graph as lg

# Load environment variables from .env file
load_dotenv()

# Get API keys
FMP_API_KEY = os.getenv("FMP_API_KEY")


@tool
def get_fundamental_analysis(company_ticker: str):
    """
    Fetch fundamental financial data like EPS, P/E ratio, revenue, and cash flow for a given company.
    """
    print(f"🔍 Fetching fundamental data for: {company_ticker}")
    financial_data = {}

    # Fetch from Yahoo Finance
    stock = yf.Ticker(company_ticker)
    print("📊 Retrieved data from Yahoo Finance.")

    # Earnings and Valuation Metrics
    financial_data['EPS'] = stock.info.get('trailingEps', None)
    financial_data['PE_Ratio'] = stock.info.get('trailingPE', None)
    financial_data['PB_Ratio'] = stock.info.get('priceToBook', None)
    financial_data['PEG_Ratio'] = stock.info.get('pegRatio', None)

    # Revenue and Growth Figures
    financial_data['Total_Revenue'] = stock.financials.loc['Total Revenue'].iloc[0] if 'Total Revenue' in stock.financials.index else None
    financial_data['Revenue_Growth'] = stock.info.get('revenueGrowth', None)

    # EPS Growth Trends (Fetch from FMP API)
    url = f"https://financialmodelingprep.com/api/v3/income-statement/{company_ticker}?apikey={FMP_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        eps_data = response.json()
        print("✅ Retrieved EPS data from FMP API.")
        try:
            eps_latest = eps_data[0].get('eps', None)
            eps_previous = eps_data[1].get('eps', None)
            financial_data['EPS_Growth_YoY'] = (
                (eps_latest - eps_previous) / eps_previous) if eps_previous else None
        except IndexError:
            financial_data['EPS_Growth_YoY'] = None
    else:
        print("⚠️ Failed to retrieve EPS data from FMP API.")

    # Profitability Metrics
    financial_data['Net_Profit_Margin'] = stock.info.get('profitMargins', None)
    financial_data['Operating_Margin'] = stock.info.get(
        'operatingMargins', None)
    financial_data['ROE'] = stock.info.get('returnOnEquity', None)
    financial_data['ROA'] = stock.info.get('returnOnAssets', None)

    # Balance Sheet Data
    financial_data['Debt_to_Equity'] = stock.info.get('debtToEquity', None)
    financial_data['Total_Assets'] = stock.balance_sheet.loc['Total Assets'].iloc[0] if 'Total Assets' in stock.balance_sheet.index else None
    financial_data['Total_Liabilities'] = stock.balance_sheet.loc['Total Liabilities'].iloc[
        0] if 'Total Liabilities' in stock.balance_sheet.index else None

    # Cash Flow Metrics (Fetch from FMP API)
    url = f"https://financialmodelingprep.com/api/v3/cash-flow-statement/{company_ticker}?apikey={FMP_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        cashflow_data = response.json()
        print("✅ Retrieved Cash Flow data from FMP API.")
        try:
            financial_data['Operating_Cash_Flow'] = cashflow_data[0].get(
                'operatingCashFlow', None)
            financial_data['Free_Cash_Flow'] = cashflow_data[0].get(
                'freeCashFlow', None)
        except IndexError:
            financial_data['Operating_Cash_Flow'] = None
            financial_data['Free_Cash_Flow'] = None
    else:
        print("⚠️ Failed to retrieve Cash Flow data from FMP API.")

    # Dividend Data
    financial_data['Dividend_Yield'] = stock.info.get('dividendYield', None)
    financial_data['Payout_Ratio'] = stock.info.get('payoutRatio', None)

    print("✅ Successfully fetched all available fundamental data.")
    return financial_data


# no need to create graph. I only need to check using this print statement
print(get_fundamental_analysis.invoke("AAPL"))
