"""Integration 도메인 예외 정의."""


class IntegrationDomainError(Exception):
    """Integration 도메인 기본 예외."""


class EndpointNotFoundError(IntegrationDomainError):
    """요청한 엔진 엔드포인트가 없을 때 발생하는 예외."""
