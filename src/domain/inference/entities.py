from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.domain.model_management import EngineType, ModelId


@dataclass(slots=True)
class InferenceRequest:
    """도메인 수준의 추론 요청 엔티티."""

    model_id: ModelId
    engine: EngineType
    prompt: str
    options: dict[str, Any]


@dataclass(slots=True)
class InferenceResponse:
    """도메인 수준의 추론 응답 엔티티."""

    model_id: ModelId
    engine: EngineType
    ok: bool
    output: dict[str, Any] | None = None
    error: str | None = None
