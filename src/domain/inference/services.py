from __future__ import annotations

from .exceptions import InvalidPromptError


class InferencePolicy:
    """추론 요청 검증과 옵션 보정을 담당하는 도메인 정책."""

    def validate_prompt(self, prompt: str) -> None:
        """프롬프트 유효성을 검증한다."""
        if not prompt or not prompt.strip():
            raise InvalidPromptError("프롬프트는 비어 있을 수 없습니다.")
        if len(prompt) > 100_000:
            raise InvalidPromptError("프롬프트 길이가 정책 제한을 초과했습니다.")

    def merge_options(self, defaults: dict[str, object], overrides: dict[str, object]) -> dict[str, object]:
        """기본 옵션과 요청 옵션을 병합한다.

        Rules:
            - `overrides` 값이 `None`인 키는 무시한다.
            - 그 외 키는 기본값을 덮어쓴다.
        """
        merged = dict(defaults)
        for key, value in overrides.items():
            if value is not None:
                merged[key] = value
        return merged
