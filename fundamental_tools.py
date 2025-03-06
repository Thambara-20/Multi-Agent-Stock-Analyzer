import os
import requests
from dotenv import load_dotenv
from langchain_community.tools import BaseTool
from langchain_core.tools import tool
import yfinance as yf

# Load environment variables from .env file
load_dotenv()

# Get API keys
FMP_API_KEY = os.getenv("FMP_API_KEY")


class FinancialFundamentalsTool(BaseTool):
    """
    A tool to fetch fundamental financial metrics for a given company ticker using Yahoo Finance and Financial Modeling Prep API.
    """
    name: str = "financial_fundamentals"
    description: str = "Fetch fundamental financial data like EPS, P/E ratio, revenue, and cash flow for a given company."

    def fetch_fmp_data(self, ticker, metric):
        """Fetch data from Financial Modeling Prep (FMP) API."""
        url = f"https://financialmodelingprep.com/api/v3/{metric}/{ticker}?apikey={FMP_API_KEY}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def _run(self, company_ticker: str):
        financial_data = {}

        # Fetch from Yahoo Finance
        stock = yf.Ticker(company_ticker)

        # Earnings and Valuation Metrics
        financial_data['EPS'] = stock.info.get('trailingEps', None)
        financial_data['PE_Ratio'] = stock.info.get('trailingPE', None)
        financial_data['PB_Ratio'] = stock.info.get('priceToBook', None)
        financial_data['PEG_Ratio'] = stock.info.get('pegRatio', None)

        # Revenue and Growth Figures
        financial_data['Total_Revenue'] = stock.financials.loc['Total Revenue'].iloc[0] if 'Total Revenue' in stock.financials.index else None
        financial_data['Revenue_Growth'] = stock.info.get(
            'revenueGrowth', None)

        # EPS Growth Trends (Fetch from FMP API)
        eps_data = self.fetch_fmp_data(company_ticker, "income-statement")
        if eps_data:
            try:
                eps_latest = eps_data[0].get('eps', None)
                eps_previous = eps_data[1].get('eps', None)
                financial_data['EPS_Growth_YoY'] = (
                    (eps_latest - eps_previous) / eps_previous) if eps_previous else None
            except IndexError:
                financial_data['EPS_Growth_YoY'] = None

        # Profitability Metrics
        financial_data['Net_Profit_Margin'] = stock.info.get(
            'profitMargins', None)
        financial_data['Operating_Margin'] = stock.info.get(
            'operatingMargins', None)
        financial_data['ROE'] = stock.info.get('returnOnEquity', None)
        financial_data['ROA'] = stock.info.get('returnOnAssets', None)

        # Balance Sheet Data
        financial_data['Debt_to_Equity'] = stock.info.get('debtToEquity', None)
        financial_data['Total_Assets'] = stock.balance_sheet.loc['Total Assets'].iloc[
            0] if 'Total Assets' in stock.balance_sheet.index else None
        financial_data['Total_Liabilities'] = stock.balance_sheet.loc['Total Liabilities'].iloc[
            0] if 'Total Liabilities' in stock.balance_sheet.index else None

        # Cash Flow Metrics (Fetch from FMP API)
        cashflow_data = self.fetch_fmp_data(
            company_ticker, "cash-flow-statement")
        if cashflow_data:
            try:
                financial_data['Operating_Cash_Flow'] = cashflow_data[0].get(
                    'operatingCashFlow', None)
                financial_data['Free_Cash_Flow'] = cashflow_data[0].get(
                    'freeCashFlow', None)
            except IndexError:
                financial_data['Operating_Cash_Flow'] = None
                financial_data['Free_Cash_Flow'] = None

        # Dividend Data
        financial_data['Dividend_Yield'] = stock.info.get(
            'dividendYield', None)
        financial_data['Payout_Ratio'] = stock.info.get('payoutRatio', None)

        return financial_data


# Example Usage
if __name__ == "__main__":
    financial_tool = FinancialFundamentalsTool()
    company_data = financial_tool._run("AAPL")  # Example for Apple Inc.
    print(company_data)
