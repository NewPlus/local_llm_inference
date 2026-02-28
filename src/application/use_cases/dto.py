from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

EngineType = Literal["ollama", "vllm"]


@dataclass(slots=True)
class EngineStatusDTO:
    """실행 중인 엔진 상태를 전달하기 위한 DTO."""

    engine: EngineType
    host: str
    port: int
    pid: int


@dataclass(slots=True)
class ModelOperationResultDTO:
    """모델 관련 명령(load/unload/apply) 실행 결과 DTO."""

    model_id: str
    engine: EngineType
    ok: bool
    message: str
    payload: dict[str, Any] | None = None


@dataclass(slots=True)
class InferenceResultDTO:
    """추론 실행 결과를 전달하기 위한 DTO."""

    model_id: str
    engine: EngineType
    ok: bool
    output: dict[str, Any] | None = None
    error: str | None = None
