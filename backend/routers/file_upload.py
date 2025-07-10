from fastapi import APIRouter, UploadFile, File
from typing import List
import io
import base64
from pdf2image import convert_from_bytes
from PIL import Image

router = APIRouter()

@router.post("/")
def upload_file(file: UploadFile = File(...)):
    """
    Accepts a PDF or image file upload. If PDF, converts each page to a PNG image. If image, returns the image as base64 PNG.
    Returns a list of base64-encoded PNG images for further processing by VLM models.
    """
    content_type = file.content_type
    result_images = []
    if content_type == "application/pdf":
        pdf_bytes = file.file.read()
        images = convert_from_bytes(pdf_bytes)
        for img in images:
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            base64_str = base64.b64encode(buf.getvalue()).decode("utf-8")
            result_images.append(base64_str)
    elif content_type.startswith("image/"):
        img = Image.open(file.file)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        base64_str = base64.b64encode(buf.getvalue()).decode("utf-8")
        result_images.append(base64_str)
    else:
        return {"error": "Unsupported file type. Please upload a PDF or image."}
    return {"images": result_images}
