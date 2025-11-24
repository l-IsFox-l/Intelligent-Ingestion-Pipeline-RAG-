# Document model for db
from sqlalchemy import Column, Integer, String, Text, Enum, DateTime
from sqlalchemy.sql import func
from ..base import Base
import enum

class ProcessingStatus(str, enum.Enum):
    """Status of document processing"""
    PENDING = 'pending' # File loaded, not processed yet
    PROCESSING = 'processing' # File is being processed
    COMPLETED = 'completed' # File processed and stored into Qdrant
    FAILED = 'failed' # Error during processing

class Document(Base):
    """Model of the loaded document"""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False) # Path to /app/temp/pdf_name.pdf
    status = Column(String, default=ProcessingStatus.PENDING, index=True) # Processing status
    content_hash = Column(String, index=True, nullable=True) # Hash of the content to avoid duplicates
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    error_message = Column(Text, nullable=True) # Store error message if processing failed
    chunk_count = Column(Integer, default=0) # Number of chunks created from the document
