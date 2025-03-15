from fastapi import APIRouter, UploadFile, Depends, Form

from .dependancies import validate_har

app = APIRouter()


@app.get("/api/health")
def health():
    return {"message": "Reverse API running.."}


@app.post("/api/process-har")
async def process_har(
    file: UploadFile = Depends(validate_har), api_description: str = Form(...)
):
    return {
        "message": f"Received file: {file.filename} and description: {api_description}"
    }
