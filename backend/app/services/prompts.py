# File with prompts for the agent

GRADE_PROMPT = (
    "You are a greder assessing relevance of a retrieved document to a user question."
    "Here is the retrieved document: \n\n {context} \n\n"
    "Here is the user question: {question} \n"
    "If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. \n"
    "Give the binary score  'yes' or 'no' to indicate whether the document is relevant to the question."
)

REWRITE_PROMPT = (
    "Look at the input and try to reason about the underlying semantic intent / meaning. \n"
    "Here is the initial question: \n"
    "{question} \n"
    "Formulate an improved question:"
)

GENERATE_PROMPT = """You are an assistant for question-answering tasks. 
Use the following pieces of retrieved context to answer the question. 
If you don't know the answer, just say that you don't know. 
Use three sentences maximum and keep the answer concise.

Question: {question} 

Context: 
{context} 

Answer:"""