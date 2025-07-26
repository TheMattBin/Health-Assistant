import os
import io
import base64
from typing import Optional
from dotenv import load_dotenv

from PIL import Image
import torch
from transformers import AutoProcessor, AutoModelForImageTextToText
from fastapi import APIRouter, UploadFile, File, Form

load_dotenv()
access_token = os.getenv("HF_TOKEN")

router = APIRouter()

# Load model and processor once at startup
model_id = "google/medgemma-4b-it"
model = AutoModelForImageTextToText.from_pretrained(
    model_id,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)
processor = AutoProcessor.from_pretrained(model_id)

def run_vlm(image: Image.Image, query: str) -> str:
    """
    Internal utility to run MedGemma VLM on a PIL image and text query.
    """
    messages = [
        {"role": "system", "content": [{"type": "text", "text": "You are an expert radiologist."}]},
        {"role": "user", "content": [
            {"type": "text", "text": query},
            {"type": "image", "image": image}
        ]}
    ]
    inputs = processor.apply_chat_template(
        messages, add_generation_prompt=True, tokenize=True,
        return_dict=True, return_tensors="pt"
    ).to(model.device, dtype=torch.bfloat16)
    input_len = inputs["input_ids"].shape[-1]
    with torch.inference_mode():
        generation = model.generate(**inputs, max_new_tokens=200, do_sample=False)
        generation = generation[0][input_len:]
    decoded = processor.decode(generation, skip_special_tokens=True)
    return decoded

# Optionally keep the /vlm-query endpoint for direct use, but main use is internal
@router.post("/vlm-query")
def vlm_query(
    image_file: UploadFile = File(...),
    query: str = Form(...)
):
    image = Image.open(io.BytesIO(image_file.file.read()))
    result = run_vlm(image, query)
    return {"result": result}
