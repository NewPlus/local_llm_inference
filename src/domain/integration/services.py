from __future__ import annotations

from src.domain.model_management import EngineType

from .entities import ApiDocLink, EngineEndpoint
from .exceptions import EndpointNotFoundError


class IntegrationPolicy:
    """엔진 엔드포인트 라우팅 및 문서 링크 생성을 담당하는 도메인 정책."""

    def resolve_targets(self, selected: list[EngineType] | None) -> list[EngineType]:
        """실행 대상 엔진 목록을 확정한다.

        Notes:
            선택이 없으면 PRD 정책에 따라 두 엔진을 모두 반환한다.
        """
        if selected:
            return selected
        return [EngineType.OLLAMA, EngineType.VLLM]

    def get_endpoint(self, endpoints: dict[EngineType, EngineEndpoint], engine: EngineType) -> EngineEndpoint:
        """엔진에 해당하는 엔드포인트를 반환한다."""
        endpoint = endpoints.get(engine)
        if endpoint is None:
            raise EndpointNotFoundError(f"엔진 엔드포인트를 찾을 수 없습니다: {engine}")
        return endpoint

    def build_doc_links(self, endpoint: EngineEndpoint, docs_paths: list[str]) -> list[ApiDocLink]:
        """엔진별 API 문서 링크 목록을 생성한다."""
        return [ApiDocLink(engine=endpoint.engine, url=f"{endpoint.base_url}{path}") for path in docs_paths]
