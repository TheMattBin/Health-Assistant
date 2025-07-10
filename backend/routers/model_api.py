from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional
from PIL import Image
import io
import torch
from transformers import AutoProcessor, AutoModelForImageTextToText
import base64

router = APIRouter()

# Load model and processor once at startup
model_id = "google/medgemma-4b-it"
model = AutoModelForImageTextToText.from_pretrained(
    model_id,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)
processor = AutoProcessor.from_pretrained(model_id)

@router.post("/vlm-query")
def vlm_query(
    image_file: UploadFile = File(...),
    query: str = Form(...)
):
    """
    Accepts an image and a text query, runs the VLM model, and returns the generated response.
    """
    image = Image.open(io.BytesIO(image_file.file.read()))
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
    return {"result": decoded}
