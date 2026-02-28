from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Prompt:
    """사용자 입력 프롬프트 값 객체."""

    text: str

    def __post_init__(self) -> None:
        if not self.text or not self.text.strip():
            raise ValueError("프롬프트는 비어 있을 수 없습니다.")


@dataclass(frozen=True, slots=True)
class InferenceOptions:
    """추론 옵션 값 객체."""

    temperature: float | None = None
    top_p: float | None = None
    num_ctx: int | None = None
    max_tokens: int | None = None
