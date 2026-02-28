class ConfigError(Exception):
    """설정 처리 과정의 기본 예외 클래스."""

    pass


class ConfigFileNotFoundError(ConfigError):
    """설정 파일이 존재하지 않을 때 발생하는 예외."""

    pass


class ConfigValidationError(ConfigError):
    """설정 값 유효성 검증에 실패했을 때 발생하는 예외."""

    pass
