# Logic for RAG agent using langgraph
from dotenv import load_dotenv
from typing import Annotated, Literal, TypedDict
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END

load_dotenv()

# Define llm
llm = ChatGroq(
    model_name = "",
    temperature=0.2
)