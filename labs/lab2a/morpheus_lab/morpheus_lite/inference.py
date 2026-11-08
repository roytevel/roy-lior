from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class InferenceRequest:
    prompt: str
    model: str | None = None
    inputs: dict[str, Any] = field(default_factory=dict)


@dataclass
class InferenceResponse:
    output: str
    provider: str
    model: str | None
    latency_ms: float
    fallback_used: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


def _deterministic_explain(request: InferenceRequest) -> str:
    inputs = request.inputs or {}
    risk = inputs.get("risk_score", 0)
    evidence = inputs.get("evidence", [])
    action = inputs.get("recommended_action", "no_action")

    evidence_text = "; ".join(evidence) if evidence else "no specific evidence items"
    return (
        f"This alert has a risk score of {risk}. "
        f"The key evidence supporting this classification includes: {evidence_text}. "
        f"Based on the Responsible AI policy, the recommended action is '{action}'. "
        f"Human review is required before any automated response is executed. "
        f"The analyst should independently verify the evidence and consider whether "
        f"the risk score is proportionate to the observed indicators."
    )


class ResilientInference:
    def __init__(self, config: dict[str, Any]) -> None:
        self._config = config
        self._provider = os.environ.get(
            "MORPHEUS_INFERENCE_PROVIDER",
            config.get("provider", "deterministic"),
        )
        self._fallback = config.get("fallback_provider", "deterministic")
        self._model = config.get("model")

    def predict(self, request: InferenceRequest) -> InferenceResponse:
        start = time.monotonic()
        fallback_used = False

        if self._provider != "deterministic":
            try:
                output = self._call_provider(request)
                provider = self._provider
            except Exception:
                output = _deterministic_explain(request)
                provider = "deterministic"
                fallback_used = True
        else:
            output = _deterministic_explain(request)
            provider = "deterministic"

        latency_ms = (time.monotonic() - start) * 1000
        return InferenceResponse(
            output=output,
            provider=provider,
            model=request.model or self._model,
            latency_ms=latency_ms,
            fallback_used=fallback_used,
        )

    def _call_provider(self, request: InferenceRequest) -> str:
        import requests as _requests

        provider = self._provider
        config = self._config

        if provider == "ollama":
            url = config.get("ollama_url", "http://localhost:11434/api/generate")
            resp = _requests.post(
                url,
                json={"model": request.model or config.get("model", "llama3"), "prompt": request.prompt, "stream": False},
                timeout=config.get("timeout_seconds", 90),
            )
            resp.raise_for_status()
            return resp.json().get("response", "")

        if provider == "nim":
            base_url = config.get("nim_base_url", "http://localhost:8000/v1")
            api_key = os.environ.get(config.get("nim_api_key_env", "NIM_API_KEY"), "")
            resp = _requests.post(
                f"{base_url}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={"model": request.model or config.get("model"), "messages": [{"role": "user", "content": request.prompt}]},
                timeout=config.get("timeout_seconds", 90),
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]

        raise ValueError(f"Unsupported provider: {provider}")
