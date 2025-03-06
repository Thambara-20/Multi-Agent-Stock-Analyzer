from langchain_core.tools import tool
from langchain_community.tools import RedditSearchRun
from typing import Annotated, Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END, MessagesState

from typing import Literal

from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.prebuilt import create_react_agent
from langgraph.types import Command

from technical_tools import calculate_technical_indicators, get_historical_prices, get_intraday_data, get_volume_data
from top_stocks import get_top_stocks


load_dotenv()
llm = ChatGroq(model="llama-3.3-70b-specdec")


workflow = StateGraph(MessagesState)

technical_analysis_tools = [calculate_technical_indicators, get_historical_prices, get_intraday_data, get_volume_data]
technical_analysis_data_collector = llm.bind_tools(technical_analysis_tools)


