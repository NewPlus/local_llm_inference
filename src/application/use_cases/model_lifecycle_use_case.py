from __future__ import annotations

from src.infrastructure import AppSettings, ConfigValidationError, EngineType, OllamaAdapter, VllmAdapter

from .dto import ModelOperationResultDTO


class ModelLifecycleUseCase:
    """모델 load/unload/list/apply 흐름을 오케스트레이션하는 유스케이스."""

    def __init__(self, settings: AppSettings) -> None:
        """엔진별 어댑터를 초기화한다."""
        self.settings = settings
        self._adapters = self._build_adapters()

    def _build_adapters(self) -> dict[EngineType, OllamaAdapter | VllmAdapter]:
        """설정의 엔드포인트 정보를 바탕으로 엔진 어댑터를 생성한다."""
        endpoints = self.settings.runtime.endpoints
        return {
            "ollama": OllamaAdapter(host=endpoints["ollama"].host, port=endpoints["ollama"].port),
            "vllm": VllmAdapter(host=endpoints["vllm"].host, port=endpoints["vllm"].port),
        }

    def _get_model_or_raise(self, model_id: str):
        """모델 ID로 설정을 조회하고, 없으면 예외를 발생시킨다."""
        model = self.settings.get_model(model_id)
        if model is None:
            raise ConfigValidationError(f"존재하지 않는 모델 ID입니다: {model_id}")
        return model

    def list(self, engine: EngineType | None = None) -> list[dict[str, object]]:
        """설정 기준 모델 목록을 반환한다."""
        models = self.settings.enabled_models(engine=engine)
        return [
            {
                "id": model.id,
                "engine": model.engine,
                "model_name": model.model_name(),
                "auto_load": model.auto_load,
                "enabled": model.enabled,
                "tags": model.tags,
            }
            for model in models
        ]

    def load(self, model_id: str) -> ModelOperationResultDTO:
        """단일 모델 로드를 수행한다."""
        model = self._get_model_or_raise(model_id)
        adapter = self._adapters[model.engine]
        response = adapter.load_model(
            model.model_name(),
            keep_alive=model.resource_policy.keep_alive,
        )
        return ModelOperationResultDTO(
            model_id=model.id,
            engine=model.engine,
            ok=response.ok,
            message="모델 로드 성공" if response.ok else "모델 로드 실패",
            payload=response.payload if response.ok else {"error": response.error},
        )

    def unload(self, model_id: str) -> ModelOperationResultDTO:
        """단일 모델 언로드를 수행한다."""
        model = self._get_model_or_raise(model_id)
        adapter = self._adapters[model.engine]
        response = adapter.unload_model(model.model_name())
        return ModelOperationResultDTO(
            model_id=model.id,
            engine=model.engine,
            ok=response.ok,
            message="모델 언로드 성공" if response.ok else "모델 언로드 실패",
            payload=response.payload if response.ok else {"error": response.error},
        )

    def apply(self) -> list[ModelOperationResultDTO]:
        """설정 동기화 정책을 적용한다.

        Rules:
            - enabled + auto_load 모델은 load
            - enabled가 아니거나 auto_load가 false면 unload
        """
        results: list[ModelOperationResultDTO] = []
        for model in self.settings.models:
            if model.enabled and model.auto_load:
                results.append(self.load(model.id))
            else:
                results.append(self.unload(model.id))
        return results
