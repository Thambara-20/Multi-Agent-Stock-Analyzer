from langchain_groq import ChatGroq
import json
import os


# Load API key for Groq (Ensure this is set in your environment variables)
# GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_KEY = "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"


def generate_weight_metrics():
    """
    Uses an LLM (Llama 3) on GroqCloud to dynamically generate weight metrics for fundamental analysis.
    Returns a dictionary with weights for different financial metrics.
    """
    llm = ChatGroq(model_name="llama3-70b-8192",
                   api_key=GROQ_API_KEY, temperature=0)

    prompt = """
    You are a financial analyst specializing in fundamental analysis.
    Your task is to assign numerical weights (between -1 and 1) to financial metrics, representing their importance in fundamental analysis.

    ### Instructions:
    - Higher positive values indicate **more importance**.
    - Negative values indicate **lower is better** (e.g., Debt-to-Equity Ratio).
    - The response **must be a valid JSON object** with metric names as keys and weights as float values.
    - Do **not** include any additional text outside the JSON.

    ### Example JSON Output:
    {
        "EPS": 0.15,
        "PE_Ratio": -0.05,
        "PB_Ratio": -0.05,
        "PEG_Ratio": -0.05,
        "Total_Revenue": 0.10,
        "Revenue_Growth": 0.15,
        "EPS_Growth_YoY": 0.10,
        "Net_Profit_Margin": 0.10,
        "Operating_Margin": 0.10,
        "ROE": 0.10,
        "ROA": 0.10,
        "Debt_to_Equity": -0.05,
        "Operating_Cash_Flow": 0.10,
        "Free_Cash_Flow": 0.10,
        "Dividend_Yield": 0.05,
        "Payout_Ratio": -0.05
    }
    """

    response = llm.invoke(prompt)

    try:
        # Convert JSON string to dictionary
        weights = json.loads(response.content)
        print("📊 LLM-Generated Weights:", weights)
        return weights
    except json.JSONDecodeError:
        print("⚠️ Error parsing LLM response, using default weights.")
        return None  # Handle fallback weights if needed
