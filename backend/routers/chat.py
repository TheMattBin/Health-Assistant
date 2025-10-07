from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from typing import Optional
from pdf2image import convert_from_bytes
from PIL import Image
import io
from routers.model_api import run_vlm
from routers.chat_history import get_user_id
from utils.file_storage import save_uploaded_file

router = APIRouter()

@router.post("/ask")
def chat_ask(file: UploadFile = File(None), question: str = Form(...), user_id: str = Depends(get_user_id)):
    images = []
    file_path = None
    original_filename = None

    if file:
        original_filename = file.filename
        content_type = file.content_type

        # Read file content for storage
        file_content = file.file.read()
        file.file.seek(0)  # Reset file pointer for processing

        if content_type == "application/pdf":
            images = convert_from_bytes(file_content)
            if not images:
                raise HTTPException(status_code=400, detail="No images found in PDF.")
        elif content_type.startswith("image/"):
            images = [Image.open(io.BytesIO(file_content))]
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Please upload a PDF or image.")

        # Save the original file
        file_path = save_uploaded_file(file_content, user_id, original_filename)

    if not images:
        answer = run_vlm(query=question)
    else:
        answer = run_vlm(images[0], question)

    return {
        "result": answer,
        "filePath": file_path,
        "fileName": original_filename
    }
