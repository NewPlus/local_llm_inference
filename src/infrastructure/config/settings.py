from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from .exceptions import ConfigValidationError

EngineType = Literal["ollama", "vllm"]
"""지원하는 추론 엔진 타입."""


@dataclass(slots=True)
class EndpointConfig:
    """엔진별 API 엔드포인트 정보."""

    host: str
    port: int


@dataclass(slots=True)
class RuntimeConfig:
    """런타임 공통 설정.

    Notes:
        `active_engines`가 비어 있으면 기본값으로 `ollama`, `vllm`을 모두 활성화한다.
    """

    python_version: str = "3.12"
    active_engines: list[EngineType] = field(default_factory=list)
    endpoints: dict[EngineType, EndpointConfig] = field(
        default_factory=lambda: {
            "ollama": EndpointConfig(host="127.0.0.1", port=11434),
            "vllm": EndpointConfig(host="127.0.0.1", port=8000),
        }
    )
    docs_paths: list[str] = field(default_factory=lambda: ["/docs", "/redoc", "/openapi.json"])

    def resolved_active_engines(self) -> list[EngineType]:
        """유효성 검증을 거친 활성 엔진 목록을 반환한다."""
        engines = self.active_engines or ["ollama", "vllm"]
        normalized: list[EngineType] = []
        for engine in engines:
            if engine not in ("ollama", "vllm"):
                raise ConfigValidationError(f"지원하지 않는 엔진: {engine}")
            if engine not in normalized:
                normalized.append(engine)
        return normalized


@dataclass(slots=True)
class ModelParameters:
    """모델 추론 파라미터 묶음."""

    temperature: float | None = None
    top_p: float | None = None
    num_ctx: int | None = None
    dtype: str | None = None
    max_model_len: int | None = None
    tensor_parallel_size: int | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "ModelParameters":
        """dict 입력을 `ModelParameters` 객체로 변환한다."""
        if not data:
            return cls()
        return cls(
            temperature=data.get("temperature"),
            top_p=data.get("top_p"),
            num_ctx=data.get("num_ctx"),
            dtype=data.get("dtype"),
            max_model_len=data.get("max_model_len"),
            tensor_parallel_size=data.get("tensor_parallel_size"),
        )


@dataclass(slots=True)
class ModelResourcePolicy:
    """모델 로드/언로드 관련 리소스 정책."""

    keep_alive: str | None = None
    unload_timeout: int | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "ModelResourcePolicy":
        """dict 입력을 `ModelResourcePolicy` 객체로 변환한다."""
        if not data:
            return cls()
        return cls(
            keep_alive=data.get("keep_alive"),
            unload_timeout=data.get("unload_timeout"),
        )


@dataclass(slots=True)
class ModelConfig:
    """단일 모델 설정 엔티티."""

    id: str
    engine: EngineType
    ollama_model: str | None = None
    vllm_model: str | None = None
    auto_load: bool = False
    parameters: ModelParameters = field(default_factory=ModelParameters)
    resource_policy: ModelResourcePolicy = field(default_factory=ModelResourcePolicy)
    enabled: bool = True
    tags: list[str] = field(default_factory=list)
    source: str | None = None

    def model_name(self) -> str:
        """엔진 타입에 맞는 실제 모델 식별자(이름)를 반환한다."""
        if self.engine == "ollama":
            if not self.ollama_model:
                raise ConfigValidationError(f"모델 {self.id}는 ollama_model 값이 필요합니다.")
            return self.ollama_model
        if not self.vllm_model:
            raise ConfigValidationError(f"모델 {self.id}는 vllm_model 값이 필요합니다.")
        return self.vllm_model

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ModelConfig":
        """dict 입력을 검증하여 `ModelConfig` 객체로 변환한다."""
        model_id = data.get("id")
        engine = data.get("engine")
        if not model_id:
            raise ConfigValidationError("models[].id는 필수입니다.")
        if engine not in ("ollama", "vllm"):
            raise ConfigValidationError(f"models[{model_id}] engine 값이 유효하지 않습니다: {engine}")

        model_config = cls(
            id=str(model_id),
            engine=engine,
            ollama_model=data.get("ollama_model"),
            vllm_model=data.get("vllm_model"),
            auto_load=bool(data.get("auto_load", False)),
            parameters=ModelParameters.from_dict(data.get("parameters")),
            resource_policy=ModelResourcePolicy.from_dict(data.get("resource_policy")),
            enabled=bool(data.get("enabled", True)),
            tags=list(data.get("tags") or []),
            source=data.get("source"),
        )
        model_config.model_name()
        return model_config


@dataclass(slots=True)
class AppSettings:
    """애플리케이션 전체 설정 루트 객체."""

    runtime: RuntimeConfig
    models: list[ModelConfig]

    def enabled_models(self, engine: EngineType | None = None) -> list[ModelConfig]:
        """활성화된 모델 목록을 반환한다.

        Args:
            engine: 지정 시 해당 엔진 모델만 필터링한다.
        """
        models = [model for model in self.models if model.enabled]
        if engine is not None:
            return [model for model in models if model.engine == engine]
        return models

    def get_model(self, model_id: str) -> ModelConfig | None:
        """모델 ID로 설정을 조회하고, 없으면 `None`을 반환한다."""
        for model in self.models:
            if model.id == model_id:
                return model
        return None
