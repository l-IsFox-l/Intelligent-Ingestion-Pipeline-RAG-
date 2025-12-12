# Code for pdf processing and saving into vector stores
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient, models

from app.core.config import settings


def get_embeddings_model():
    """Initialize and return the embeddings model"""
    return HuggingFaceEmbeddings(
        model_name=settings.EMBEDDINGS_MODEL_NAME,
        model_kwargs={"device": "cpu"}
        )

def get_qdrant_client():
    """Initialize and return the Qdrant client"""
    return QdrantClient(
        host=settings.QDRANT_HOST,
        port=settings.QDRANT_PORT
    )

def get_retriever():
    """Function for retriever"""
    qdrant_client = get_qdrant_client()
    embeddings = get_embeddings_model()
    collection_name = "documents_collection"
    if not qdrant_client.collection_exists(collection_name):
        print(f"Collection {collection_name} doesn't exist, creating new empty collection...")

        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=384, # size of all-MiniLM-l6-v2
                distance=models.Distance.COSINE
            )
        )
        print(f"Empty collection {collection_name} created!")

    vector_store = QdrantVectorStore(
        client=qdrant_client,
        collection_name="documents_collection",
        embedding=embeddings,

    )
    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    return retriever

def define_retriever_tool():
    """Define retriever tool for agent"""
    retriever = get_retriever()
    retriever_tool = retriever.as_tool(
        name="Document_retriever",
        description="Useful for retvieving document chunks relevant to the user's query."
    )
    
    return retriever_tool


def process_document(file_path: str, doc_id: int) -> dict:
    """Function for documents processing:
    - load pdf
    - chunk and embed
    - save into vector store
    """
    try:
        loader = PyPDFLoader(file_path)
        raw_docs = loader.load()
    except Exception as e:
        raise ValueError(f"Error loading PDF file: {str(e)}")
    
    if not raw_docs:
        raise ValueError("No content found in the PDF file.")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 1000,
        chunk_overlap = 200,
        add_start_index = True
    )

    chunks = text_splitter.split_documents(raw_docs)

    # Addinf metadata to chunks
    for chunk in chunks:
        chunk.metadata["document_id"] = doc_id
        chunk.metadata["source"] = file_path

    embeddings = get_embeddings_model()

    vector_store = QdrantVectorStore.from_documents(
        documents=chunks,
        embedding=embeddings,
        host=settings.QDRANT_HOST,
        port=settings.QDRANT_PORT,
        collection_name="documents_collection",
        force_recreate=False
    )

    # Return statistics
    return {
        "status": "succes",
        "chunks_count": len(chunks)
    }