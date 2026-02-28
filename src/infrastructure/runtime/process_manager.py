from __future__ import annotations

import subprocess
from dataclasses import dataclass

from ..config.settings import AppSettings, EngineType, ModelConfig


@dataclass(slots=True)
class EngineProcessInfo:
    """실행 중인 엔진 프로세스 메타데이터."""

    engine: EngineType
    host: str
    port: int
    pid: int


class ProcessManager:
    """추론 엔진 프로세스의 기동/중지/상태 조회를 담당한다."""

    def __init__(self, settings: AppSettings) -> None:
        """설정을 기반으로 프로세스 매니저를 초기화한다."""
        self.settings = settings
        self._processes: dict[EngineType, subprocess.Popen[str]] = {}

    def resolve_engines(self, selected_engines: list[EngineType] | None = None) -> list[EngineType]:
        """실행 대상 엔진 목록을 확정한다.

        Notes:
            `selected_engines`가 없으면 설정의 기본 정책(미설정 시 ollama+vllm 동시)을 따른다.
        """
        if selected_engines:
            return selected_engines
        return self.settings.runtime.resolved_active_engines()

    def _first_enabled_model(self, engine: EngineType) -> ModelConfig | None:
        """엔진별로 사용할 대표 활성 모델 1개를 선택한다."""
        models = self.settings.enabled_models(engine=engine)
        if not models:
            return None
        auto_models = [model for model in models if model.auto_load]
        return auto_models[0] if auto_models else models[0]

    def _build_ollama_command(self) -> list[str]:
        """Ollama 서버 기동 커맨드를 생성한다."""
        return ["ollama", "serve"]

    def _build_vllm_command(self, model_name: str, host: str, port: int) -> list[str]:
        """vLLM(OpenAI 호환) 서버 기동 커맨드를 생성한다."""
        return [
            "python3.12",
            "-m",
            "vllm.entrypoints.openai.api_server",
            "--model",
            model_name,
            "--host",
            host,
            "--port",
            str(port),
        ]

    def start_engines(self, selected_engines: list[EngineType] | None = None) -> dict[EngineType, EngineProcessInfo]:
        """엔진 프로세스를 시작하고 PID/포트 정보를 반환한다."""
        active_engines = self.resolve_engines(selected_engines)
        started: dict[EngineType, EngineProcessInfo] = {}

        for engine in active_engines:
            endpoint = self.settings.runtime.endpoints[engine]

            if engine == "ollama":
                command = self._build_ollama_command()
            else:
                model = self._first_enabled_model("vllm")
                if model is None:
                    raise RuntimeError("vLLM 기동을 위한 활성 모델이 없습니다.")
                command = self._build_vllm_command(
                    model_name=model.model_name(),
                    host=endpoint.host,
                    port=endpoint.port,
                )

            process = subprocess.Popen(command, text=True)
            self._processes[engine] = process
            started[engine] = EngineProcessInfo(
                engine=engine,
                host=endpoint.host,
                port=endpoint.port,
                pid=process.pid,
            )

        return started

    def stop_engine(self, engine: EngineType) -> None:
        """단일 엔진 프로세스를 안전하게 종료한다."""
        process = self._processes.get(engine)
        if process is None:
            return
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=10)
        self._processes.pop(engine, None)

    def stop_all(self) -> None:
        """관리 중인 모든 엔진 프로세스를 종료한다."""
        for engine in list(self._processes):
            self.stop_engine(engine)

    def status(self) -> list[EngineProcessInfo]:
        """현재 실행 중인 엔진 프로세스 상태 목록을 반환한다."""
        result: list[EngineProcessInfo] = []
        for engine, process in self._processes.items():
            endpoint = self.settings.runtime.endpoints[engine]
            if process.poll() is None:
                result.append(
                    EngineProcessInfo(
                        engine=engine,
                        host=endpoint.host,
                        port=endpoint.port,
                        pid=process.pid,
                    )
                )
        return result
