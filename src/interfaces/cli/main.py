from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from src.application.use_cases import EngineSelectionUseCase, InferenceUseCase, ModelLifecycleUseCase
from src.infrastructure import AppSettings, load_settings


def _load_app_settings(config_path: str) -> AppSettings:
    """설정 파일을 로드해 애플리케이션 설정 객체를 반환한다."""
    return load_settings(Path(config_path))


def _print_json(data: Any) -> None:
    """객체를 JSON 형태로 출력한다."""
    print(json.dumps(data, ensure_ascii=False, indent=2, default=str))


def _to_jsonable(obj: Any) -> Any:
    """dataclass(slots 포함) 객체를 JSON 직렬화 가능한 형태로 변환한다."""
    if is_dataclass(obj):
        return asdict(obj)
    return obj


def _parse_engines(raw: str | None) -> list[str] | None:
    """콤마 구분 엔진 문자열을 리스트로 변환한다."""
    if raw is None or raw.strip() == "":
        return None
    return [engine.strip() for engine in raw.split(",") if engine.strip()]


def build_parser() -> argparse.ArgumentParser:
    """CLI 인자 파서를 구성한다."""
    parser = argparse.ArgumentParser(description="로컬 LLM 추론 서버 제어 CLI")
    parser.add_argument("--config", default="config/models.yml", help="설정 파일 경로")

    subparsers = parser.add_subparsers(dest="command", required=True)

    serve_parser = subparsers.add_parser("serve", help="엔진을 기동하고 포그라운드로 유지")
    serve_parser.add_argument("--engines", help="기동할 엔진 목록 (예: ollama,vllm)")

    start_parser = subparsers.add_parser("start", help="엔진을 기동하고 종료")
    start_parser.add_argument("--engines", help="기동할 엔진 목록 (예: ollama,vllm)")

    stop_parser = subparsers.add_parser("stop", help="엔진 중지")
    stop_parser.add_argument("--engine", help="중지할 엔진 (ollama 또는 vllm)")
    stop_parser.add_argument("--all", action="store_true", help="모든 엔진 중지")

    subparsers.add_parser("status", help="현재 프로세스 기준 엔진 상태 조회")

    health_parser = subparsers.add_parser("health", help="엔진 헬스 체크")
    health_parser.add_argument("--engine", help="검사할 엔진 (생략 시 전체 정책 대상)")

    models_parser = subparsers.add_parser("models", help="모델 목록 조회")
    models_parser.add_argument("--engine", help="필터할 엔진 (ollama 또는 vllm)")

    load_parser = subparsers.add_parser("load", help="모델 로드")
    load_parser.add_argument("model_id", help="로드할 모델 ID")

    unload_parser = subparsers.add_parser("unload", help="모델 언로드")
    unload_parser.add_argument("model_id", help="언로드할 모델 ID")

    down_parser = subparsers.add_parser("down", help="활성 모델 전체 언로드")
    down_parser.add_argument("--engine", help="언로드할 엔진 필터 (ollama 또는 vllm)")

    subparsers.add_parser("apply", help="YAML 정책 기준 모델 동기화 실행")

    infer_parser = subparsers.add_parser("infer", help="단일 추론 요청")
    infer_parser.add_argument("--model-id", required=True, help="추론에 사용할 모델 ID")
    infer_parser.add_argument("--prompt", required=True, help="사용자 프롬프트")
    infer_parser.add_argument("--temperature", type=float)
    infer_parser.add_argument("--top-p", type=float)
    infer_parser.add_argument("--num-ctx", type=int)
    infer_parser.add_argument("--max-tokens", type=int)
    infer_parser.add_argument("--timeout", type=int, help="추론 요청 타임아웃(초)")

    return parser


def main() -> None:
    """CLI 명령을 실행한다."""
    parser = build_parser()
    args = parser.parse_args()

    settings = _load_app_settings(args.config)
    engine_use_case = EngineSelectionUseCase(settings)
    model_use_case = ModelLifecycleUseCase(settings)
    inference_use_case = InferenceUseCase(settings)

    if args.command == "serve":
        engines = _parse_engines(args.engines)
        statuses = engine_use_case.start(selected_engines=engines)
        _print_json([_to_jsonable(status) for status in statuses])
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            engine_use_case.stop_all()
            print("엔진을 모두 중지했습니다.")
        return

    if args.command == "start":
        engines = _parse_engines(args.engines)
        statuses = engine_use_case.start(selected_engines=engines)
        _print_json([_to_jsonable(status) for status in statuses])
        return

    if args.command == "stop":
        if args.all:
            engine_use_case.stop_all()
            _print_json({"ok": True, "message": "모든 엔진 중지 완료"})
            return
        if args.engine:
            engine_use_case.stop(args.engine)
            _print_json({"ok": True, "message": f"엔진 중지 완료: {args.engine}"})
            return
        parser.error("stop 명령은 --engine 또는 --all 이 필요합니다.")

    if args.command == "status":
        statuses = engine_use_case.status()
        _print_json([_to_jsonable(status) for status in statuses])
        return

    if args.command == "health":
        result = inference_use_case.health(engine=args.engine)
        _print_json(result)
        return

    if args.command == "models":
        result = model_use_case.list(engine=args.engine)
        _print_json(result)
        return

    if args.command == "load":
        result = model_use_case.load(args.model_id)
        _print_json(_to_jsonable(result))
        return

    if args.command == "unload":
        result = model_use_case.unload(args.model_id)
        _print_json(_to_jsonable(result))
        return

    if args.command == "down":
        result = model_use_case.unload_all(engine=args.engine)
        _print_json([_to_jsonable(item) for item in result])
        return

    if args.command == "apply":
        result = model_use_case.apply()
        _print_json([_to_jsonable(item) for item in result])
        return

    if args.command == "infer":
        result = inference_use_case.generate(
            model_id=args.model_id,
            prompt=args.prompt,
            temperature=args.temperature,
            top_p=args.top_p,
            num_ctx=args.num_ctx,
            max_tokens=args.max_tokens,
            timeout=args.timeout,
        )
        _print_json(_to_jsonable(result))
        return


if __name__ == "__main__":
    main()
