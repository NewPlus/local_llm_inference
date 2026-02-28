from __future__ import annotations

from pathlib import Path

from src.infrastructure import AppSettings, load_settings

from .dto import EngineStatusDTO
from .engine_selection_use_case import EngineSelectionUseCase


class StartupUseCase:
    """앱 시작 시 설정 로딩과 엔진 기동을 수행하는 유스케이스."""

    def __init__(self, config_path: str | Path) -> None:
        """설정 파일 경로를 받아 내부 설정을 로딩한다."""
        self.config_path = Path(config_path)
        self.settings: AppSettings = load_settings(self.config_path)
        self.engine_use_case = EngineSelectionUseCase(self.settings)

    def start(self) -> list[EngineStatusDTO]:
        """기본 정책에 따라 엔진을 기동하고 상태를 반환한다."""
        return self.engine_use_case.start()

    def stop(self) -> None:
        """기동된 엔진을 모두 중지한다."""
        self.engine_use_case.stop_all()
