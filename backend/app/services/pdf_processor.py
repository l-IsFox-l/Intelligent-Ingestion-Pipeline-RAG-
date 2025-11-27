# Code for pdf processing and saving into vector stores
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from app.core.config import settings


# TODO:
def get_embeddings_model():
    """Initialize and return the embeddings model"""
    return HuggingFaceEmbeddings(
        model_name=settings.EMBEDDINGS_MODEL_NAME,
        model_kwargs={"device": "cpu"}
        )

# Set up qdrant client
def get_qdrant_client():
    """Initialize and return the Qdrant client"""
    return QdrantClient(
        host=settings.QDRANT_HOST,
        port=settings.QDRANT_PORT
    )


# - process pdf for chunking:
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