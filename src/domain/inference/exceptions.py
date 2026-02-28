"""Inference 도메인 예외 정의."""


class InferenceDomainError(Exception):
    """Inference 도메인 기본 예외."""


class InvalidPromptError(InferenceDomainError):
    """프롬프트가 정책을 위반했을 때 발생하는 예외."""
