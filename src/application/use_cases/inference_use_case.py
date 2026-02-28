from __future__ import annotations

from typing import Any

from src.infrastructure import AppSettings, ConfigValidationError, EngineType, OllamaAdapter, VllmAdapter

from .dto import InferenceResultDTO


class InferenceUseCase:
    """모델 추론과 엔진 헬스 체크를 담당하는 유스케이스."""

    def __init__(self, settings: AppSettings) -> None:
        """엔진별 어댑터를 초기화한다."""
        self.settings = settings
        endpoints = self.settings.runtime.endpoints
        self._adapters: dict[EngineType, OllamaAdapter | VllmAdapter] = {
            "ollama": OllamaAdapter(host=endpoints["ollama"].host, port=endpoints["ollama"].port),
            "vllm": VllmAdapter(host=endpoints["vllm"].host, port=endpoints["vllm"].port),
        }

    def health(self, engine: EngineType | None = None) -> dict[str, dict[str, Any]]:
        """엔진 헬스 상태를 조회한다.

        Args:
            engine: 지정하면 해당 엔진만 검사하고, 없으면 전체 활성 엔진을 검사한다.
        """
        targets = [engine] if engine else self.settings.runtime.resolved_active_engines()
        result: dict[str, dict[str, Any]] = {}

        for target in targets:
            response = self._adapters[target].health_check()
            result[target] = {
                "ok": response.ok,
                "payload": response.payload,
                "error": response.error,
            }

        return result

    def generate(self, model_id: str, prompt: str, **kwargs: Any) -> InferenceResultDTO:
        """지정 모델로 추론을 수행한다."""
        model = self.settings.get_model(model_id)
        if model is None:
            raise ConfigValidationError(f"존재하지 않는 모델 ID입니다: {model_id}")

        adapter = self._adapters[model.engine]
        response = adapter.generate(
            model_name=model.model_name(),
            prompt=prompt,
            temperature=kwargs.get("temperature", model.parameters.temperature),
            top_p=kwargs.get("top_p", model.parameters.top_p),
            num_ctx=kwargs.get("num_ctx", model.parameters.num_ctx),
            max_tokens=kwargs.get("max_tokens"),
        )

        return InferenceResultDTO(
            model_id=model.id,
            engine=model.engine,
            ok=response.ok,
            output=response.payload,
            error=response.error,
        )
