from fastapi import FastAPI, File, UploadFile, Depends
from app.core.config import settings

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.session import get_db



app = FastAPI(title=settings.PROJECT_NAME)

# Endpoints
@app.get("/int-rag")
def int_rag():
    return{"message": "testing..."}

@app.post("/upload-file")
def upload_file(file: UploadFile = File(...)):
    """Endpoint to upload a pdf file."""
    # TODO: Write custom function to clear pdf from unuseful data, chunk, store in db and vector store (in another file)
    return{"filename": file.filename, "content_type": file.content_type}

@app.get("/check_bd")
async def check_bd(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("SELECT 1"))
        return {"status": "ok", "db_response": result.scalar()}
    except Exception as e:
        return {"status": "error", "detail": str(e)}