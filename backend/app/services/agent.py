# Logic for RAG agent using langgraph
from dotenv import load_dotenv
from typing import Annotated, Literal, TypedDict
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from app.core.config import settings

load_dotenv()

# Define llm
llm = ChatGroq(
    model_name = settings.LLM_NAME,
    temperature=0.2
)