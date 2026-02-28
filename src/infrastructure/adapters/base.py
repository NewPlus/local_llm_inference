from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class AdapterResponse:
    """엔진 어댑터의 공통 응답 형식.

    Attributes:
        ok: 요청 성공 여부.
        payload: 성공 시 반환되는 응답 데이터.
        error: 실패 시 오류 메시지.
    """

    ok: bool
    payload: dict[str, Any] | None = None
    error: str | None = None


class EngineAdapter(ABC):
    """Ollama/vLLM 등 추론 엔진 어댑터의 공통 인터페이스."""

    def __init__(self, host: str, port: int) -> None:
        """엔진 접속 정보(host/port)를 초기화한다."""
        self.host = host
        self.port = port

    @property
    @abstractmethod
    def engine(self) -> str:
        """어댑터가 담당하는 엔진 식별자(예: ollama, vllm)를 반환한다."""
        raise NotImplementedError

    @property
    def base_url(self) -> str:
        """엔진 API의 기본 URL을 반환한다."""
        return f"http://{self.host}:{self.port}"

    @abstractmethod
    def health_check(self) -> AdapterResponse:
        """엔진 헬스 체크를 수행한다."""
        raise NotImplementedError

    @abstractmethod
    def list_models(self) -> AdapterResponse:
        """엔진에서 사용 가능한 모델 목록을 조회한다."""
        raise NotImplementedError

    @abstractmethod
    def load_model(self, model_name: str, **kwargs: Any) -> AdapterResponse:
        """지정한 모델을 로드(또는 워밍업)한다."""
        raise NotImplementedError

    @abstractmethod
    def unload_model(self, model_name: str, **kwargs: Any) -> AdapterResponse:
        """지정한 모델을 언로드(또는 비활성화)한다."""
        raise NotImplementedError

    @abstractmethod
    def generate(self, model_name: str, prompt: str, **kwargs: Any) -> AdapterResponse:
        """모델 추론 요청을 실행하고 결과를 반환한다."""
        raise NotImplementedError
