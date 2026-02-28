from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .base import AdapterResponse, EngineAdapter


class VllmAdapter(EngineAdapter):
    """vLLM(OpenAI 호환 API)와 통신하는 인프라 어댑터."""

    @property
    def engine(self) -> str:
        """어댑터 엔진 식별자 값을 반환한다."""
        return "vllm"

    def _request(self, path: str, method: str = "GET", payload: dict[str, Any] | None = None) -> AdapterResponse:
        """vLLM API로 HTTP 요청을 보내고 표준 응답으로 변환한다."""
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
        """vLLM 헬스 체크를 수행한다."""
        response = self._request("/health")
        if response.ok and response.payload == {}:
            return AdapterResponse(ok=True, payload={"status": "ok"})
        return response

    def list_models(self) -> AdapterResponse:
        """vLLM의 OpenAI 호환 모델 목록을 조회한다."""
        return self._request("/v1/models")

    def load_model(self, model_name: str, **kwargs: Any) -> AdapterResponse:
        """vLLM의 모델 로드 정책(프로세스 기동 시 지정)을 설명용 응답으로 반환한다."""
        return AdapterResponse(
            ok=True,
            payload={
                "message": "vLLM 모델 로딩은 프로세스 시작 시 모델 지정으로 처리됩니다.",
                "model": model_name,
            },
        )

    def unload_model(self, model_name: str, **kwargs: Any) -> AdapterResponse:
        """vLLM의 모델 언로드 정책(프로세스 종료 기반)을 설명용 응답으로 반환한다."""
        return AdapterResponse(
            ok=True,
            payload={
                "message": "vLLM 모델 언로드는 프로세스 종료 정책으로 처리됩니다.",
                "model": model_name,
            },
        )

    def generate(self, model_name: str, prompt: str, **kwargs: Any) -> AdapterResponse:
        """OpenAI 호환 `/v1/chat/completions`로 채팅 추론을 실행한다."""
        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": kwargs.get("temperature"),
            "top_p": kwargs.get("top_p"),
            "max_tokens": kwargs.get("max_tokens"),
        }
        return self._request("/v1/chat/completions", method="POST", payload=payload)
