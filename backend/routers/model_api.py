import os
import io
from PIL import Image
from dotenv import load_dotenv
from fastapi import APIRouter, UploadFile, File, Form

import torch
from transformers import AutoProcessor, AutoModelForImageTextToText

load_dotenv()
access_token = os.getenv("HF_TOKEN")

router = APIRouter()

model_id = "google/medgemma-4b-it"
model = AutoModelForImageTextToText.from_pretrained(
    model_id,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)
processor = AutoProcessor.from_pretrained(model_id)

def run_vlm(image: Image.Image = None, query: str = "") -> str:
    user_content = [{"type": "text", "text": query}]
    if image:
        user_content.append({"type": "image", "image": image})

    messages = [
        {"role": "system", "content": [{"type": "text", "text": "You are an expert radiologist."}]},
        {"role": "user", "content": user_content}
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

@router.post("/vlm-query")
def vlm_query(
    image_file: UploadFile = File(...),
    query: str = Form(...)
):
    image = Image.open(io.BytesIO(image_file.file.read()))
    result = run_vlm(image, query)
    return {"result": result}
