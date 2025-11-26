import os
import uuid
import hashlib
import aiofiles # For habdling async file load
from fastapi import FastAPI, File, UploadFile, Depends, HTTPException
from app.core.config import settings
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.models.document import Document
from app.worker.tasks import process_document_task

os.makedirs(settings.UPLOAD_DIR, exist_ok=True) # Creates a folder for temps files if doesn't exist

app = FastAPI(title=settings.PROJECT_NAME)
# Endpoints
@app.get("/int-rag")
def int_rag():
    return{"message": "testing..."}

@app.post("/upload-file")
async def upload_file(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
    ):
    """Endpoint to upload a pdf file."""

    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF format files allowed!")

    # Generating uuid to allow multiple files with the same name
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)

    file_content_hash = hashlib.sha256()

    try:
        async with aiofiles.open(file_path, "wb") as user_file:
            while content := await file.read(1024*1024):
                file_content_hash.update(content)
                await user_file.write(content)
        
        # Getting full hash
        content_hash = file_content_hash.hexdigest()

        # Checking for dublicates
        query = select(Document).where(Document.content_hash == content_hash)
        result = await db.execute(query)
        exiting_doc = result.scalar_one_or_none()

        if exiting_doc: # if dublicate
            os.remove(file_path)

            return {
                "task_id": exiting_doc.id,
                "filename": exiting_doc.filename,
                "status": exiting_doc.status,
                "original_id": exiting_doc.id
            }
        
        # if original
        new_doc = Document(
            filename=file.filename,
            filepath=file_path,
            content_hash=content_hash,
            status="pending"
        )

        db.add(new_doc)
        await db.commit()
        await db.refresh(new_doc)

        process_document_task.delay(doc_id = new_doc.id)

        return{
            "task_id": new_doc.id,
            "filename": new_doc.filename,
            "status": "uploaded"
        }

    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/check_bd")
async def check_bd(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("SELECT 1"))
        return {"status": "ok", "db_response": result.scalar()}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
    
@app.get("/status/{task_id}")
async def get_status(task_id: int, db: AsyncSession = Depends(get_db)):
    """Endpoint to get the status of document processing task"""
    query = select(Document).where(Document.id == task_id)
    result = await db.execute(query)
    doc = result.scalar_one_or_none()
    
    if not doc:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {
        "task_id": doc.id,
        "status": doc.status,
        "filename": doc.filename,
        "chunks": doc.chunk_count,
        "error": doc.error_message
    }