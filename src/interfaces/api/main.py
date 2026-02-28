from __future__ import annotations

from contextlib import asynccontextmanager
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.application.use_cases import EngineSelectionUseCase, InferenceUseCase, ModelLifecycleUseCase
from src.infrastructure import AppSettings, load_settings


def _load_app_settings(config_path: str | Path = "config/models.yml") -> AppSettings:
    """API 서버에서 사용할 설정을 로드한다."""
    return load_settings(config_path)


def _to_jsonable(obj: Any) -> Any:
    """dataclass(slots 포함) 객체를 JSON 직렬화 가능한 형태로 변환한다."""
    if is_dataclass(obj):
        return asdict(obj)
    return obj


class EngineStartRequest(BaseModel):
    """엔진 시작 요청 바디 모델."""

    engines: list[Literal["ollama", "vllm"]] | None = None


class InferenceRequestBody(BaseModel):
    """추론 요청 바디 모델."""

    model_id: str
    prompt: str
    temperature: float | None = None
    top_p: float | None = None
    num_ctx: int | None = None
    max_tokens: int | None = None
    timeout: int | None = None


class ModelUnloadAllRequest(BaseModel):
    """모델 일괄 언로드 요청 바디 모델."""

    engine: Literal["ollama", "vllm"] | None = None


class AppContainer:
    """API 핸들러에서 사용할 유스케이스 컨테이너."""

    def __init__(self, settings: AppSettings) -> None:
        self.settings = settings
        self.engine = EngineSelectionUseCase(settings)
        self.model = ModelLifecycleUseCase(settings)
        self.inference = InferenceUseCase(settings)


def create_app(config_path: str | Path = "config/models.yml") -> FastAPI:
    """FastAPI 애플리케이션을 생성한다."""
    settings = _load_app_settings(config_path)
    container = AppContainer(settings)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        print("[API DOCS] 접근 가능한 문서 경로")
        print("- /docs")
        print("- /redoc")
        print("- /openapi.json")
        yield

    app = FastAPI(
        title="Local LLM Inference API",
        description="Ollama + vLLM 기반 로컬 추론 제어 API",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.state.container = container

    @app.get("/health")
    def health(engine: Literal["ollama", "vllm"] | None = None) -> dict[str, dict[str, Any]]:
        return app.state.container.inference.health(engine=engine)

    @app.post("/engines/start")
    def start_engines(request: EngineStartRequest) -> list[dict[str, Any]]:
        statuses = app.state.container.engine.start(selected_engines=request.engines)
        return [_to_jsonable(status) for status in statuses]

    @app.get("/engines/status")
    def engine_status() -> list[dict[str, Any]]:
        statuses = app.state.container.engine.status()
        return [_to_jsonable(status) for status in statuses]

    @app.post("/engines/stop/{engine}")
    def stop_engine(engine: Literal["ollama", "vllm"]) -> dict[str, Any]:
        app.state.container.engine.stop(engine)
        return {"ok": True, "engine": engine}

    @app.post("/engines/stop")
    def stop_all_engines() -> dict[str, Any]:
        app.state.container.engine.stop_all()
        return {"ok": True}

    @app.get("/models")
    def list_models(engine: Literal["ollama", "vllm"] | None = None) -> list[dict[str, Any]]:
        return app.state.container.model.list(engine=engine)

    @app.post("/models/{model_id}/load")
    def load_model(model_id: str) -> dict[str, Any]:
        try:
            result = app.state.container.model.load(model_id)
            return _to_jsonable(result)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/models/{model_id}/unload")
    def unload_model(model_id: str) -> dict[str, Any]:
        try:
            result = app.state.container.model.unload(model_id)
            return _to_jsonable(result)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/models/unload")
    def unload_all_models(request: ModelUnloadAllRequest) -> list[dict[str, Any]]:
        try:
            results = app.state.container.model.unload_all(engine=request.engine)
            return [_to_jsonable(item) for item in results]
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/models/apply")
    def apply_models() -> list[dict[str, Any]]:
        try:
            results = app.state.container.model.apply()
            return [_to_jsonable(item) for item in results]
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/inference")
    def infer(request: InferenceRequestBody) -> dict[str, Any]:
        try:
            result = app.state.container.inference.generate(
                model_id=request.model_id,
                prompt=request.prompt,
                temperature=request.temperature,
                top_p=request.top_p,
                num_ctx=request.num_ctx,
                max_tokens=request.max_tokens,
                timeout=request.timeout,
            )
            return _to_jsonable(result)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    return app


app = create_app()
