from __future__ import annotations

from abc import ABC, abstractmethod

from src.domain.model_management import EngineType

from .entities import EngineEndpoint


class EngineEndpointRepository(ABC):
    """엔진 엔드포인트 조회를 위한 저장소 인터페이스."""

    @abstractmethod
    def get(self, engine: EngineType) -> EngineEndpoint | None:
        """엔진 식별자로 엔드포인트를 조회한다."""
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> list[EngineEndpoint]:
        """전체 엔드포인트 목록을 반환한다."""
        raise NotImplementedError
