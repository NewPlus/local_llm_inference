from __future__ import annotations

from abc import ABC, abstractmethod

from .entities import ModelAggregate
from .value_objects import ModelId


class ModelRepository(ABC):
    """모델 메타데이터 저장소 인터페이스."""

    @abstractmethod
    def get(self, model_id: ModelId) -> ModelAggregate | None:
        """모델 ID로 단일 모델을 조회한다."""
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> list[ModelAggregate]:
        """전체 모델 목록을 조회한다."""
        raise NotImplementedError


class ModelStateRepository(ABC):
    """모델 런타임 상태 저장소 인터페이스."""

    @abstractmethod
    def save_state(self, aggregate: ModelAggregate) -> None:
        """모델 상태를 저장한다."""
        raise NotImplementedError
