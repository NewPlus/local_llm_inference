from __future__ import annotations

from dataclasses import dataclass, field

from .exceptions import InvalidModelStateError
from .value_objects import EngineType, ModelId, ModelLifecycleState


@dataclass(slots=True)
class ModelAggregate:
    """모델 메타데이터와 라이프사이클 상태를 표현하는 애그리거트."""

    model_id: ModelId
    engine: EngineType
    model_name: str
    auto_load: bool = False
    enabled: bool = True
    state: ModelLifecycleState = field(default=ModelLifecycleState.UNLOADED)

    def mark_loaded(self) -> None:
        """모델 상태를 LOADED로 전이한다."""
        if not self.enabled:
            raise InvalidModelStateError("비활성 모델은 로드할 수 없습니다.")
        self.state = ModelLifecycleState.LOADED

    def mark_unloaded(self) -> None:
        """모델 상태를 UNLOADED로 전이한다."""
        self.state = ModelLifecycleState.UNLOADED

    def should_be_loaded(self) -> bool:
        """정책상 로드 유지 대상인지 판단한다."""
        return self.enabled and self.auto_load
