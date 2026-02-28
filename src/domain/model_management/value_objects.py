from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class EngineType(StrEnum):
    """시스템이 지원하는 추론 엔진 타입."""

    OLLAMA = "ollama"
    VLLM = "vllm"


class ModelLifecycleState(StrEnum):
    """모델 라이프사이클 상태."""

    LOADED = "loaded"
    UNLOADED = "unloaded"


@dataclass(frozen=True, slots=True)
class ModelId:
    """모델을 식별하기 위한 값 객체."""

    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("ModelId는 비어 있을 수 없습니다.")
