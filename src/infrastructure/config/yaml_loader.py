from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .exceptions import ConfigFileNotFoundError, ConfigValidationError
from .settings import AppSettings, EndpointConfig, ModelConfig, RuntimeConfig


def _parse_runtime(data: dict[str, Any] | None) -> RuntimeConfig:
    """`runtime` 섹션을 파싱해 `RuntimeConfig`로 변환한다."""
    runtime_data = data or {}

    python_version = str(runtime_data.get("python_version", "3.12"))
    if python_version != "3.12":
        raise ConfigValidationError(f"python_version은 3.12만 허용됩니다. 현재 값: {python_version}")

    active_engines = list(runtime_data.get("active_engines") or [])

    endpoint_data = runtime_data.get("endpoints") or {}
    ollama_data = endpoint_data.get("ollama") or {}
    vllm_data = endpoint_data.get("vllm") or {}

    endpoints = {
        "ollama": EndpointConfig(
            host=str(ollama_data.get("host", "127.0.0.1")),
            port=int(ollama_data.get("port", 11434)),
        ),
        "vllm": EndpointConfig(
            host=str(vllm_data.get("host", "127.0.0.1")),
            port=int(vllm_data.get("port", 8000)),
        ),
    }

    docs_paths = list(runtime_data.get("docs_paths") or ["/docs", "/redoc", "/openapi.json"])

    runtime = RuntimeConfig(
        python_version=python_version,
        active_engines=active_engines,
        endpoints=endpoints,
        docs_paths=docs_paths,
    )
    runtime.resolved_active_engines()
    return runtime


def _parse_models(data: list[dict[str, Any]] | None) -> list[ModelConfig]:
    """`models` 섹션을 파싱해 모델 설정 목록으로 변환한다."""
    models_data = data or []
    models = [ModelConfig.from_dict(item) for item in models_data]
    if not models:
        raise ConfigValidationError("최소 1개 이상의 모델 정의가 필요합니다.")
    return models


def load_settings(config_path: str | Path) -> AppSettings:
    """YAML 설정 파일을 읽어 애플리케이션 설정 객체를 생성한다.

    Args:
        config_path: YAML 파일 경로.

    Returns:
        파싱/검증이 완료된 `AppSettings` 객체.
    """
    path = Path(config_path)
    if not path.exists():
        raise ConfigFileNotFoundError(f"설정 파일을 찾을 수 없습니다: {path}")

    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        raise ConfigValidationError("설정 파일 최상위는 매핑(dict)이어야 합니다.")

    runtime = _parse_runtime(raw.get("runtime"))
    models = _parse_models(raw.get("models"))
    return AppSettings(runtime=runtime, models=models)
