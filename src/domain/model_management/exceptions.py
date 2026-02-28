"""ModelManagement 도메인 예외 정의."""


class ModelManagementDomainError(Exception):
    """ModelManagement 도메인 기본 예외."""


class InvalidModelStateError(ModelManagementDomainError):
    """모델 상태 전이가 유효하지 않을 때 발생하는 예외."""


class ModelNotFoundError(ModelManagementDomainError):
    """요청한 모델을 찾을 수 없을 때 발생하는 예외."""
