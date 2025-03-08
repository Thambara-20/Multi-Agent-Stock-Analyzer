from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    ToolMessage,
    AIMessage  # if you ever need to add an AI message manually
)
from main import graph

# Initialize FastAPI app
app = FastAPI()

# Define response model
class ResponseModel(BaseModel):
    messages: List[str]

@app.get("/analyze")
async def analyze_market() -> ResponseModel:
    """
    FastAPI endpoint to process stock market analysis with a fixed message.
    """
    # Use a fixed message
    initial_messages = [HumanMessage(content="Analyze the US stock market and give me the best stocks for today.")]
    initial_state = {"messages": initial_messages}

    # Invoke the workflow
    final_state = graph.invoke(initial_state)

    # Extract messages from final state
    response_messages = [msg.content for msg in final_state["messages"]]

    return ResponseModel(messages=response_messages)

# Run the server using: uvicorn filename:app --reload
