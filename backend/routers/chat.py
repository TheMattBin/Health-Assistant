from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from pdf2image import convert_from_bytes
from PIL import Image
import io
from routers.model_api import run_vlm

router = APIRouter()

# Stub for chat endpoints
@router.post("/ask")
def chat_ask(file: UploadFile = File(...), question: str = Form(...)):
    """
    Accepts a PDF or image and a user question. Converts PDF to image if needed, then queries the VLM model.
    Returns the model's answer.
    """
    content_type = file.content_type
    images = []
    if content_type == "application/pdf":
        pdf_bytes = file.file.read()
        images = convert_from_bytes(pdf_bytes)
        if not images:
            raise HTTPException(status_code=400, detail="No images found in PDF.")
    elif content_type.startswith("image/"):
        images = [Image.open(file.file)]
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type. Please upload a PDF or image.")
    # For demo, use only the first image
    answer = run_vlm(images[0], question)
    return {"result": answer}
