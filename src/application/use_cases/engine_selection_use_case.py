from __future__ import annotations

from src.infrastructure import ApiDocsPublisher, AppSettings, EngineType, ProcessManager

from .dto import EngineStatusDTO


class EngineSelectionUseCase:
    """엔진 선택 정책과 기동/중지 흐름을 제어하는 유스케이스."""

    def __init__(self, settings: AppSettings) -> None:
        """설정 기반으로 프로세스 매니저와 문서 퍼블리셔를 구성한다."""
        self.settings = settings
        self.process_manager = ProcessManager(settings)
        self.docs_publisher = ApiDocsPublisher(settings.runtime.docs_paths)

    def resolve_engines(self, selected_engines: list[EngineType] | None = None) -> list[EngineType]:
        """실행 대상 엔진 목록을 확정한다.

        Notes:
            선택값이 없으면 PRD 정책에 따라 `ollama`와 `vllm`을 모두 활성화한다.
        """
        return self.process_manager.resolve_engines(selected_engines)

    def start(self, selected_engines: list[EngineType] | None = None) -> list[EngineStatusDTO]:
        """선택 엔진(또는 기본 엔진들)을 기동하고 상태 목록을 반환한다."""
        process_infos = self.process_manager.start_engines(selected_engines)
        statuses = [
            EngineStatusDTO(
                engine=info.engine,
                host=info.host,
                port=info.port,
                pid=info.pid,
            )
            for info in process_infos.values()
        ]

        for status in statuses:
            self.docs_publisher.publish(host=status.host, port=status.port)

        return statuses

    def stop(self, engine: EngineType) -> None:
        """단일 엔진을 중지한다."""
        self.process_manager.stop_engine(engine)

    def stop_all(self) -> None:
        """관리 중인 모든 엔진을 중지한다."""
        self.process_manager.stop_all()

    def status(self) -> list[EngineStatusDTO]:
        """현재 실행 중인 엔진 상태 목록을 조회한다."""
        return [
            EngineStatusDTO(engine=info.engine, host=info.host, port=info.port, pid=info.pid)
            for info in self.process_manager.status()
        ]
