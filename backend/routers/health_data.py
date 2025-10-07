import io
import base64
from typing import List
from pdf2image import convert_from_bytes
from fastapi import APIRouter, UploadFile, File

router = APIRouter()

# Stub for health data endpoints
@router.get("/")
def get_health_data():
    return {"msg": "Health data endpoint (stub)"}

@router.post("/pdf-to-images", response_model=List[str])
def pdf_to_images(file: UploadFile = File(...)):
    """
    Accepts a PDF file upload, converts each page to a PNG image, and returns a list of base64-encoded images.
    """
    pdf_bytes = file.file.read()
    images = convert_from_bytes(pdf_bytes)
    base64_images = []
    for img in images:
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        base64_str = base64.b64encode(buf.getvalue()).decode("utf-8")
        base64_images.append(base64_str)
    return base64_images
