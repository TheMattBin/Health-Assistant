from fastapi import APIRouter, UploadFile, File, Depends
from typing import List
import io
import base64
from pdf2image import convert_from_bytes
from PIL import Image
from routers.chat_history import get_user_id
from utils.file_storage import save_uploaded_file

router = APIRouter()

@router.post("/")
def upload_file(file: UploadFile = File(...), user_id: str = Depends(get_user_id)):
    """
    Accepts a PDF or image file upload. If PDF, converts each page to a PNG image. If image, returns the image as base64 PNG.
    Also saves the original file to storage.
    Returns a list of base64-encoded PNG images for further processing by VLM models, plus file storage info.
    """
    content_type = file.content_type
    original_filename = file.filename
    result_images = []

    # Read file content for storage and processing
    file_content = file.file.read()
    file.file.seek(0)  # Reset file pointer for image processing

    if content_type == "application/pdf":
        images = convert_from_bytes(file_content)
        for img in images:
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            base64_str = base64.b64encode(buf.getvalue()).decode("utf-8")
            result_images.append(base64_str)
    elif content_type.startswith("image/"):
        img = Image.open(io.BytesIO(file_content))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        base64_str = base64.b64encode(buf.getvalue()).decode("utf-8")
        result_images.append(base64_str)
    else:
        return {"error": "Unsupported file type. Please upload a PDF or image."}

    # Save the original file
    file_path = save_uploaded_file(file_content, user_id, original_filename)

    return {
        "images": result_images,
        "filePath": file_path,
        "fileName": original_filename
    }
