# Celery worker for RAG
import logging
import asyncio
from app.core.celery_app import celery_app
from app.db.session import AsyncSessionLocal
from app.db.models.document import Document
from sqlalchemy import select

logging.basicConfig(level=logging.INFO)

@celery_app.task(name="process_document")
def process_document_task(doc_id: int):
    asyncio.run(run_rag_doc_processing(doc_id))

async def run_rag_doc_processing(doc_id: int):
    """Full RAG pipeline for document processing"""
    logging.info("RAG pipeline started!")
    # TODO: 
    # GET doc by id from bd and update status to 'processing'
    # Call pdf processing functions and save into vector store
    # Return result so user can query
    pass