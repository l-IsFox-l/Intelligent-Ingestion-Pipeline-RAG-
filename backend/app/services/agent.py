# Logic for RAG agent using langgraph
from dotenv import load_dotenv
from typing import Annotated, Literal, TypedDict, List
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langgraph.graph.message import add_messages
from langchain.messages import HumanMessage, SystemMessage, AnyMessage
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from app.core.config import settings
from app.services.pdf_processor import define_retriever_tool
from app.services.prompts import GRADE_PROMPT, REWRITE_PROMPT, GENERATE_PROMPT

load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[List[AnyMessage],add_messages]

# Define instance of tool
retriever_tool_instance = define_retriever_tool()

class GradeDocuments(BaseModel):
    """Grade documents using a binary score for relevance check."""

    binary_score: str = Field(description="Relevance score: 'yes' if relevant, or 'no' if not relevant.")

# Define llm
llm = ChatGroq(
    model_name = settings.LLM_NAME,
    temperature=0.2
)

# Node for generating query or respond
def generate_query_or_respond(state: AgentState):
    """Call the model to generate a response based on the current state. Give the question, it will decide to retrieve using tool or answer directly."""
    messages = state.get("messages", [])

    if not messages:
        return {"messages": [HumanMessage(content="Error: Empty message history.")]}
    
    response = (
        llm.bind_tools([retriever_tool_instance]).invoke(state["messages"])
    )
    return {"messages": [response]}


# Node for grading documents
def grade_documents(state: MessagesState) -> Literal["generate_answer", "rewrite_question"]:
    """Determine whether the retrieved documents are relevant to the question."""
    question = state["messages"][0].content
    context = state["messages"][-1].content

    prompt = GRADE_PROMPT.format(question=question, context=context)
    response =(
        llm.with_structured_output(GradeDocuments).invoke([HumanMessage(content=prompt)])
    )
    score = response.binary_score
    print(f"DEBUG: Document Relevance Score: {score}")

    if score.lower() == "yes":
        return "generate_answer"
    else:
        print("DEBUG: Documents irrelevant, rewriting question...")
        return "rewrite_question"
    

# Node for rewriting question
def rewrite_question(state: MessagesState):
    """Rewrite the original user question."""
    messages = state["messages"]
    question = messages[0].content

    prompt = REWRITE_PROMPT.format(question=question)
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"messages": [HumanMessage(content=response.content)]}

# Node for answer generation
def generate_answer(state: MessagesState):
    """Generate an answer."""
    question = state["messages"][0].content
    context = state["messages"][-1].content

    print(f"DEBUG: Generating answer...")
    print(f"DEBUG: Context length: {len(context)} characters")
    print(f"DEBUG: Context snippet: {context[:200]}...")
    
    prompt = GENERATE_PROMPT.format(question=question, context=context)
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"messages": [response]}

def create_graph():
    """Graph function"""
    workflow = StateGraph(AgentState)

    # Define the nodes
    workflow.add_node(generate_query_or_respond)
    workflow.add_node("retrieve", ToolNode([retriever_tool_instance]))
    workflow.add_node(rewrite_question)
    workflow.add_node(generate_answer)

    workflow.add_edge(START, "generate_query_or_respond")

    workflow.add_conditional_edges(
        "generate_query_or_respond",
        
        tools_condition,
        {
            "tools": "retrieve",
            END: END,
        },
    )

    workflow.add_conditional_edges(
        "retrieve",
        grade_documents,
    )

    workflow.add_edge("generate_answer", END)
    workflow.add_edge("rewrite_question", "generate_query_or_respond")

    graph = workflow.compile()

    return graph