from fastapi import FastAPI



app = FastAPI()

# Endpoints
@app.get("/int-rag")
def int_rag():
    return{"message": "testing..."}