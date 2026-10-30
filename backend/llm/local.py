"""MedGemma running locally through transformers.

Optional: install with `uv sync --extra local` and set LLM_PROVIDER=local.
torch/transformers are imported only when this provider is created, so the
default (OpenRouter) setup needs neither a GPU nor the heavy dependencies.
"""

from time import perf_counter
from typing import List, Optional

from PIL import Image

from .base import LLMResult

MODEL_ID = "google/medgemma-4b-it"


class LocalMedGemmaLLM:
    def __init__(self, model_id: str = MODEL_ID, max_new_tokens: int = 200):
        import torch
        from transformers import AutoModelForImageTextToText, AutoProcessor

        self.name = "local"
        self.models = [model_id]
        self._torch = torch
        self._max_new_tokens = max_new_tokens
        self._model = AutoModelForImageTextToText.from_pretrained(
            model_id, torch_dtype=torch.bfloat16, device_map="auto"
        )
        self._processor = AutoProcessor.from_pretrained(model_id)

    def complete(
        self, messages: List[dict], images: Optional[List[Image.Image]] = None
    ) -> LLMResult:
        started = perf_counter()
        chat = [
            {"role": m["role"], "content": [{"type": "text", "text": m["content"]}]}
            for m in messages
        ]
        for image in images or []:
            chat[-1]["content"].append({"type": "image", "image": image})

        inputs = self._processor.apply_chat_template(
            chat, add_generation_prompt=True, tokenize=True, return_dict=True, return_tensors="pt"
        ).to(self._model.device, dtype=self._torch.bfloat16)
        input_len = inputs["input_ids"].shape[-1]
        with self._torch.inference_mode():
            generation = self._model.generate(
                **inputs, max_new_tokens=self._max_new_tokens, do_sample=False
            )
        text = self._processor.decode(generation[0][input_len:], skip_special_tokens=True)
        return LLMResult(
            text=text, model=self.models[0], latency_ms=int((perf_counter() - started) * 1000)
        )
