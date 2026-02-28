from __future__ import annotations

from dataclasses import dataclass

from src.domain.model_management import EngineType


@dataclass(frozen=True, slots=True)
class EngineEndpoint:
    """엔진 API 엔드포인트 도메인 엔티티."""

    engine: EngineType
    host: str
    port: int

    @property
    def base_url(self) -> str:
        """엔진 기본 URL을 반환한다."""
        return f"http://{self.host}:{self.port}"


@dataclass(frozen=True, slots=True)
class ApiDocLink:
    """API 문서 링크 엔티티."""

    engine: EngineType
    url: str
