# Celery worker for RAG
import logging
import asyncio
from app.core.celery_app import celery_app
from app.db.session import AsyncSessionLocal
from app.db.models.document import Document
from sqlalchemy import select
from app.services.pdf_processor import process_document

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@celery_app.task(name="process_document")
def process_document_task(doc_id: int):
    try:
        asyncio.run(run_rag_doc_processing(doc_id))
    except Exception as e:
        logger.error(f"Worker error: {str(e)}")

async def run_rag_doc_processing(doc_id: int):
    """Full RAG pipeline for document processing"""
    
    logger.info("RAG doc processing pipeline started!")

    async with AsyncSessionLocal() as db:
        query = select(Document).where(Document.id == doc_id)
        result = await db.execute(query)
        doc = result.scalar_one_or_none()

        if not doc:
            logger.error(f"Document with id {doc_id} not found in database.")
            return

        logger.info(f"Processing document: {doc.filename}")
        doc.status = "processing"
        await db.commit()

        try:
            stats = await asyncio.to_thread(process_document, doc.filepath, doc.id)
            
            # If successful
            doc.status = "completed"
            doc.chunk_count = stats["chunk_count"]
            doc.error_message = None

            logger.info(f"Document {doc.filename} processed successfully! Chunks: {stats['chunks_count']}")

        # If not successful
        except Exception as e:
            logger.error(f"Failed to process document {doc.filename}: {str(e)}")
            doc.status = "failed"
            doc.error_message = str(e)

        finally:
            await db.commit()