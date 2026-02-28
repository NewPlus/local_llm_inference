from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .base import AdapterResponse, EngineAdapter


class OllamaAdapter(EngineAdapter):
    """Ollama HTTP API와 통신하는 인프라 어댑터."""

    @property
    def engine(self) -> str:
        """어댑터 엔진 식별자 값을 반환한다."""
        return "ollama"

    def _request(self, path: str, method: str = "GET", payload: dict[str, Any] | None = None) -> AdapterResponse:
        """Ollama API로 HTTP 요청을 보내고 표준 응답으로 변환한다."""
        url = f"{self.base_url}{path}"
        data = None
        headers = {"Content-Type": "application/json"}

        if payload is not None:
            data = json.dumps(payload).encode("utf-8")

        request = Request(url=url, data=data, headers=headers, method=method)

        try:
            with urlopen(request, timeout=10) as response:
                body = response.read().decode("utf-8")
                if body:
                    return AdapterResponse(ok=True, payload=json.loads(body))
                return AdapterResponse(ok=True, payload={})
        except HTTPError as exc:
            return AdapterResponse(ok=False, error=f"HTTPError {exc.code}: {exc.reason}")
        except URLError as exc:
            return AdapterResponse(ok=False, error=f"URLError: {exc.reason}")
        except Exception as exc:
            return AdapterResponse(ok=False, error=str(exc))

    def health_check(self) -> AdapterResponse:
        """Ollama 서버 상태를 확인한다."""
        return self._request("/api/tags")

    def list_models(self) -> AdapterResponse:
        """Ollama에 등록된 모델 목록을 조회한다."""
        return self._request("/api/tags")

    def load_model(self, model_name: str, **kwargs: Any) -> AdapterResponse:
        """지정 모델을 keep_alive 옵션으로 메모리에 유지하도록 요청한다."""
        payload = {
            "model": model_name,
            "prompt": kwargs.get("prompt", ""),
            "stream": False,
            "keep_alive": kwargs.get("keep_alive", "30m"),
        }
        return self._request("/api/generate", method="POST", payload=payload)

    def unload_model(self, model_name: str, **kwargs: Any) -> AdapterResponse:
        """keep_alive=0 요청으로 모델 언로드를 유도한다."""
        payload = {
            "model": model_name,
            "prompt": "",
            "stream": False,
            "keep_alive": 0,
        }
        return self._request("/api/generate", method="POST", payload=payload)

    def generate(self, model_name: str, prompt: str, **kwargs: Any) -> AdapterResponse:
        """Ollama `/api/generate` 엔드포인트로 비스트리밍 추론을 실행한다."""
        payload = {
            "model": model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature"),
                "top_p": kwargs.get("top_p"),
                "num_ctx": kwargs.get("num_ctx"),
            },
        }
        return self._request("/api/generate", method="POST", payload=payload)
