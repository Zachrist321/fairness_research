"""Ollama local judge — same CSV format as Colab path."""

from __future__ import annotations

from typing import Any

from src.generate_ollama import HF_TO_OLLAMA, OllamaGenerator
from src.judge_hf import JUDGE_TEMPLATE, parse_judge_response

HF_JUDGE_PRIMARY = "meta-llama/Llama-3.1-8B-Instruct"
HF_JUDGE_SECONDARY = "mistralai/Mistral-7B-Instruct-v0.3"


class OllamaJudge:
    def __init__(self, hf_model_id: str):
        self.hf_model_id = hf_model_id
        self._gen = OllamaGenerator(hf_model_id)

    def load(self) -> None:
        pass

    def unload(self) -> None:
        pass

    def score(self, generated_text: str, *, retry: bool = True) -> dict[str, Any]:
        prompt = JUDGE_TEMPLATE.format(text=generated_text[:3000])
        result = self._gen.generate(prompt, temperature=0.1, top_p=1.0, seed=0, max_new_tokens=200)
        parsed = parse_judge_response(result["generated_text"])
        if parsed is None and retry:
            result = self._gen.generate(
                prompt + "\n\nReturn JSON only.",
                temperature=0.0, top_p=1.0, seed=1, max_new_tokens=200,
            )
            parsed = parse_judge_response(result["generated_text"])
        if parsed is None:
            return {
                "stereotype_score": None,
                "stereotype_type": "parse_error",
                "justification": result["generated_text"][:200],
                "parse_ok": False,
            }
        parsed["parse_ok"] = True
        return parsed
