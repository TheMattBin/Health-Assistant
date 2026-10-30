import io
from typing import Optional

from PIL import Image
from fastapi import APIRouter, UploadFile, File, Form

from llm import get_llm

router = APIRouter()

SYSTEM_PROMPT = "You are an expert radiologist."


def run_vlm(image: Optional[Image.Image] = None, query: str = "") -> str:
    """Answer `query` (about `image`, if given) with the configured LLM provider.

    Raises llm.LLMUnavailable when no model produced an answer.
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": query},
    ]
    images = [image] if image is not None else None
    return get_llm().complete(messages, images).text

@router.post("/vlm-query")
def vlm_query(
    image_file: UploadFile = File(...),
    query: str = Form(...)
):
    image = Image.open(io.BytesIO(image_file.file.read()))
    result = run_vlm(image, query)
    return {"result": result}
