from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from src.domain.model_management import EngineType


class InferenceGateway(ABC):
    """추론 엔진 호출을 추상화한 도메인 게이트웨이 인터페이스."""

    @abstractmethod
    def health(self, engine: EngineType) -> dict[str, Any]:
        """엔진 헬스 상태를 반환한다."""
        raise NotImplementedError

    @abstractmethod
    def generate(self, engine: EngineType, model_name: str, prompt: str, **kwargs: Any) -> dict[str, Any]:
        """엔진에 추론 요청을 위임하고 결과를 반환한다."""
        raise NotImplementedError
