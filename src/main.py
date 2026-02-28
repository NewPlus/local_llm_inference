from __future__ import annotations

import argparse
import os
import sys


def main() -> None:
    """애플리케이션 실행 모드를 선택한다."""
    parser = argparse.ArgumentParser(description="Local LLM Inference 실행 진입점")
    parser.add_argument("mode", choices=["cli", "api"], help="실행 모드")
    parser.add_argument("args", nargs=argparse.REMAINDER, help="하위 모드 인자")
    parsed = parser.parse_args()

    if parsed.mode == "cli":
        from src.interfaces.cli.main import main as cli_main

        sys.argv = ["local-llm-cli", *parsed.args]
        cli_main()
        return

    from uvicorn import run

    host = "0.0.0.0"
    port = int(os.getenv("LOCAL_LLM_API_PORT", "18080"))
    print("[API DOCS] 접근 가능한 문서 경로")
    print(f"- http://127.0.0.1:{port}/docs")
    print(f"- http://127.0.0.1:{port}/redoc")
    print(f"- http://127.0.0.1:{port}/openapi.json")
    run("src.interfaces.api.main:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    main()
