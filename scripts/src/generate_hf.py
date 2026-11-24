"""Hugging Face text generation with temperature, top_p, and seed control."""

from __future__ import annotations

import gc
import re
from typing import Any

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

REFUSAL_PATTERNS = [
    r"i can't (?:help|assist|write)",
    r"i cannot (?:help|assist|write)",
    r"as an ai",
    r"i'm not able to",
    r"i am not able to",
    r"against my guidelines",
]


def is_refusal(text: str) -> bool:
    lower = text.lower().strip()
    if len(lower) < 20:
        return True
    return any(re.search(p, lower) for p in REFUSAL_PATTERNS)


class HFGenerator:
    def __init__(self, model_id: str, *, load_in_4bit: bool = True):
        self.model_id = model_id
        self.load_in_4bit = load_in_4bit
        self.model = None
        self.tokenizer = None

    def load(self) -> None:
        if self.model is not None:
            return
        quant = None
        if self.load_in_4bit and torch.cuda.is_available():
            quant = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4",
            )
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id, token=True)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        kwargs: dict[str, Any] = {"token": True, "device_map": "auto"}
        if quant:
            kwargs["quantization_config"] = quant
        else:
            kwargs["torch_dtype"] = torch.float16 if torch.cuda.is_available() else torch.float32
        self.model = AutoModelForCausalLM.from_pretrained(self.model_id, **kwargs)

    def unload(self) -> None:
        del self.model
        del self.tokenizer
        self.model = None
        self.tokenizer = None
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    def generate(
        self,
        prompt_text: str,
        *,
        temperature: float,
        top_p: float,
        seed: int,
        max_new_tokens: int = 400,
    ) -> dict:
        self.load()
        assert self.model and self.tokenizer

        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)

        messages = [{"role": "user", "content": prompt_text}]
        if hasattr(self.tokenizer, "apply_chat_template"):
            input_text = self.tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True,
            )
        else:
            input_text = prompt_text

        inputs = self.tokenizer(input_text, return_tensors="pt").to(self.model.device)
        input_len = inputs["input_ids"].shape[1]

        with torch.no_grad():
            out = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                temperature=max(temperature, 0.01),
                top_p=top_p,
                pad_token_id=self.tokenizer.eos_token_id,
            )

        new_tokens = out[0][input_len:]
        text = self.tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
        token_count = len(new_tokens)
        word_count = len(text.split())
        truncated = token_count >= max_new_tokens - 5

        return {
            "generated_text": text,
            "token_count": int(token_count),
            "word_count": word_count,
            "refusal_flag": int(is_refusal(text)),
            "truncated_flag": int(truncated),
        }
