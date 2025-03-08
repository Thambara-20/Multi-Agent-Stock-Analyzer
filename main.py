from typing import Literal
from dotenv import load_dotenv

# LangGraph & LLM
from langgraph.graph import StateGraph, START, END, MessagesState
from langchain_groq import ChatGroq
from langsmith import trace
# Messages
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    ToolMessage,
    AIMessage  # if you ever need to add an AI message manually
)

# Example Tools
from technical_tools import (
    calculate_technical_indicators,
    get_historical_prices,
    get_volume_data,
)
from fundamental.fundamental_analysis import rank_companies
from top_stocks import get_top_stocks
from sentiment_analysis.sentiment_analysis import perform_market_research
import langsmith

# 1) Load environment variables
load_dotenv()

# 2) Initialize the LLM
llm = ChatGroq(model="llama-3.3-70b-specdec")

import os

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_PROJECT"] = "stock-market-analysis"

from langchain_google_genai import ChatGoogleGenerativeAI

# llm = ChatGoogleGenerativeAI(
#     model="gemini-1.5-pro",
#     temperature=0.7,
#     max_tokens=None,
#     timeout=None,
#     max_retries=2,
# )


# 3) Bind tools to the LLM. That way the LLM can call them if it sees fit.
technical_analysis_tools = [
    calculate_technical_indicators,
    get_historical_prices,
    get_volume_data, 
]

tools_by_name = {
    "calculate_technical_indicators": calculate_technical_indicators,
    "get_historical_prices": get_historical_prices,
    "get_volume_data": get_volume_data,
    
}

# A "tool-enabled" version of the LLM:
tool_enabled_llm = llm.bind_tools(technical_analysis_tools)

# 4) Create the Graph using MessagesState
workflow = StateGraph(MessagesState)

# -----------------------------------------------------------------------
# Define our NODES
# -----------------------------------------------------------------------

def technical_analysis_data_collector(state: MessagesState) -> MessagesState:
    """
    1) Add a system message that instructs the LLM on the role (TA expert).
    2) Append LLM's response to the conversation.
    """
    old_messages = state["messages"]
    top_stocks = get_top_stocks(5)
    
    # We can prepend a SystemMessage for context:
    system_prompt = SystemMessage(
    content=(
        "Your goal is to retrieve stock data (technical and fundamental) "
        "for the following top stocks using the provided tools: "
        + ", ".join(top_stocks)
        + ""
        " Do not provide financial advice or commentary. If data is already available for a stock, do not re-fetch it."
    )
)


    
    # The LLM sees your system message plus everything so far:
    new_llm_response = tool_enabled_llm.invoke([system_prompt])

    # Return updated conversation with the new LLM message appended
    return {
        "messages": old_messages + [new_llm_response]
    }


def should_continue(state: MessagesState) -> Literal["tool_node", "do_technical_analysis"]:
    """
    If the last LLM message has tool calls, route to the tool_node.
    Otherwise, aggregate data.
    """
    last_message = state["messages"][-1]
    tool_calls = getattr(last_message, "tool_calls", None)
    if tool_calls:
        return "tool_node"
    return "do_technical_analysis"


def tool_node(state: MessagesState) -> MessagesState:
    old_messages = state["messages"]
    last_message = old_messages[-1]
    tool_calls = getattr(last_message, "tool_calls", [])

    if not tool_calls:
        print("No tool calls found in last message.")
        return {"messages": old_messages}

    tool_outputs = []
    for call in tool_calls:
        try:
            name = call["name"]
            args = call["args"]
            
            print(f"Invoking tool: {name} with args: {args}")  # Log function calls

            tool = tools_by_name.get(name)
            if not tool:
                print(f"[Warning] No matching tool found: {name}")
                continue
        
            result = tool.invoke(args)  # Ensure correct argument passing
            tool_outputs.append(
                ToolMessage(content=str(result), tool_call_id=call["id"])
            )
        except Exception as e:
            print(f"Error invoking tool {name}: {e}")

    return {"messages": old_messages + tool_outputs}


def do_fundemental_analysis(state: MessagesState) -> MessagesState:
    print("Performing fundamental analysis...")
    top_stocks = get_top_stocks(10)
    ranked_companies = rank_companies(top_stocks)
    return {
        "messages": state["messages"] + [SystemMessage(content=f"Fundamental analysis complete. Ranked Companies: {ranked_companies}")]
    }


def do_sentimental_analysis(state: MessagesState) -> MessagesState:
    """
    Perform market research using sentiment analysis.
    """
    print("Performing market research...")
    articles = perform_market_research()
    print(f"Found {len(articles)} articles.")
    return {
        "messages": state["messages"] + [SystemMessage(content=f"Market research complete. Found {len(articles)} articles.")]
    }
    
    

def do_technical_analysis(state: MessagesState) -> MessagesState:
    """
    Aggregates data from previous messages and uses LLM to generate a summary.
    """
    old_messages = state["messages"]

    # Gather only relevant messages (Tool & System Messages)
    relevant_messages = [
        msg.content for msg in old_messages if isinstance(msg, (SystemMessage, ToolMessage))
    ]

    # Format the prompt for the LLM
    prompt = SystemMessage(
        content=(
            "Summarize the following technical analysis data and identify the top 10 stocks:\n\n"
            + "\n".join(relevant_messages) +
            "\n\nProvide a concise summary and list the top 05 stock tickers based on relevance."
        )
    )

    # Invoke the LLM to generate a summary
    summary_response = llm.invoke([prompt])
    
    print(f"LLM Summary: {summary_response.content}")

    # Append the LLM-generated summary to the conversation
    return {
        "messages": old_messages + [summary_response]
    }



def aggregate_data(state: MessagesState) -> MessagesState:
    """
    Final step: we 'aggregate' data. For demonstration, we simply call get_top_stocks()
    and append a final SystemMessage summarizing them. 
    """
    old_messages = state["messages"]

    # Gather only relevant messages (Tool & System Messages)
    relevant_messages = [
        msg.content for msg in old_messages if isinstance(msg, (SystemMessage, ToolMessage))
    ]

    # Format the prompt for the LLM
    prompt = SystemMessage(
        content=(
            "Summarize the following technical analysis data and identify the top 10 stocks:\n\n"
            + "\n".join(relevant_messages) +
            "\n\nProvide a concise summary and list the top 05 stock tickers based on relevance."
        )
    )

    # Invoke the LLM to generate a summary
    summary_response = llm.invoke([prompt])
    
    print(f"LLM Summary: {summary_response.content}")

    # Append the LLM-generated summary to the conversation
    return {
        "messages": old_messages + [summary_response]
    }

# -----------------------------------------------------------------------
# Build the Graph
# -----------------------------------------------------------------------
workflow.add_node("ta_dc", technical_analysis_data_collector)
workflow.add_node("tool_node", tool_node)
workflow.add_node("do_technical_analysis", do_technical_analysis)
workflow.add_node("do_fundemental_analysis", do_fundemental_analysis)
workflow.add_node("do_sentimental_analysis", do_sentimental_analysis)
workflow.add_node("aggregate_data", aggregate_data)

# Edges: start -> ta_dc
workflow.add_edge(START, "ta_dc")

# After the collector, conditionally route to "tool_node" or "do_technical_analysis"
workflow.add_conditional_edges("ta_dc", should_continue, {
    "tool_node": "tool_node",
    "do_technical_analysis": "do_technical_analysis"
})

# After tool_node, you could either loop back to ta_dc or just end.
# For demonstration, let's go from tool_node straight to "do_technical_analysis".
# workflow.add_edge("tool_node", "ta_dc")

# Finally, from "do_technical_analysis" -> END
# workflow.add_edge("do_technical_analysis", END)
workflow.add_edge(START, "do_fundemental_analysis")
workflow.add_edge(START, "do_sentimental_analysis")

workflow.add_edge("do_fundemental_analysis", "aggregate_data")
workflow.add_edge("do_sentimental_analysis", "aggregate_data")
workflow.add_edge("do_technical_analysis", "aggregate_data")
workflow.add_edge("aggregate_data", END)

# 5) Compile the Workflow
graph = workflow.compile()

if __name__ == "__main__":
    # 6) (Optional) Generate a diagram
    try:
        img_data = graph.get_graph().draw_mermaid_png()
        with open("graph_output.png", "wb") as f:
            f.write(img_data)
        print("Workflow diagram saved to graph_output.png")
    except Exception as e:
        print(f"Error generating diagram: {e}")

    # 7) Test with an initial user prompt
    initial_messages = [
        HumanMessage(content="Analyze the US stock market and give me the best stocks for today.")
    ]

    # The graph expects a dictionary with "messages" for MessagesState:
    initial_state = {"messages": initial_messages}

    # Invoke the workflow
    final_state = graph.invoke(initial_state)

    # 8) Print the entire conversation from final_state
    print("=== FINAL CONVERSATION ===")
    # for i, msg in enumerate(final_state["messages"]):
    #     print(f"Message {i} ({type(msg).__name__}): {msg.content}")


    with open("output.txt", "w", encoding="utf-8") as file:
        file.write("=== FINAL CONVERSATION ===\n")
        for i, msg in enumerate(final_state["messages"]):
            file.write(f"Message {i} ({type(msg).__name__}): {msg.content}\n")
