"""Ollama local generation — same checkpoint format as Colab/HuggingFace path."""

from __future__ import annotations

import ollama

from src.generate_hf import is_refusal

HF_TO_OLLAMA = {
    "meta-llama/Llama-3.1-8B-Instruct": "llama3.1:8b",
    "mistralai/Mistral-7B-Instruct-v0.3": "mistral:7b",
    "Qwen/Qwen2.5-7B-Instruct": "qwen2.5:7b",
}


class OllamaGenerator:
    def __init__(self, hf_model_id: str):
        self.hf_model_id = hf_model_id
        self.ollama_model = HF_TO_OLLAMA.get(hf_model_id)
        if not self.ollama_model:
            raise ValueError(f"No Ollama mapping for {hf_model_id}")

    def load(self) -> None:
        pass  # Ollama loads on first request

    def unload(self) -> None:
        pass

    def generate(
        self,
        prompt_text: str,
        *,
        temperature: float,
        top_p: float,
        seed: int,
        max_new_tokens: int = 400,
    ) -> dict:
        response = ollama.generate(
            model=self.ollama_model,
            prompt=prompt_text,
            options={
                "temperature": max(float(temperature), 0.01),
                "top_p": float(top_p),
                "seed": int(seed),
                "num_predict": int(max_new_tokens),
            },
        )
        text = (response.get("response") or "").strip()
        token_count = response.get("eval_count") or len(text.split())
        word_count = len(text.split())
        truncated = int(token_count) >= max_new_tokens - 5

        return {
            "generated_text": text,
            "token_count": int(token_count),
            "word_count": word_count,
            "refusal_flag": int(is_refusal(text)),
            "truncated_flag": int(truncated),
        }
