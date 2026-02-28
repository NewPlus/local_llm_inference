from __future__ import annotations

from .entities import ModelAggregate


class ModelLifecyclePolicy:
    """모델 로드/언로드 대상 선정을 담당하는 도메인 정책 서비스."""

    def classify(self, models: list[ModelAggregate]) -> tuple[list[ModelAggregate], list[ModelAggregate]]:
        """모델 목록을 로드 대상/언로드 대상으로 분류한다."""
        to_load: list[ModelAggregate] = []
        to_unload: list[ModelAggregate] = []

        for model in models:
            if model.should_be_loaded():
                to_load.append(model)
            else:
                to_unload.append(model)

        return to_load, to_unload
