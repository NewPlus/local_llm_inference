#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

ENV_NAME="${LOCAL_LLM_CONDA_ENV:-local-llm-inference}"
PYTHON_BIN="${LOCAL_LLM_PYTHON_BIN:-}"

usage() {
  cat <<'EOF'
Usage:
  ./scripts/run_local_llm.sh cli [CLI_ARGS...]
  ./scripts/run_local_llm.sh api

Examples:
  ./scripts/run_local_llm.sh cli --help
  ./scripts/run_local_llm.sh cli start
  ./scripts/run_local_llm.sh cli down
  ./scripts/run_local_llm.sh cli down --engine ollama
  ./scripts/run_local_llm.sh cli infer --model-id qwen-27b-ollama --prompt "안녕"
  ./scripts/run_local_llm.sh api

Options (environment variables):
  LOCAL_LLM_CONDA_ENV   사용할 conda 환경 이름 (기본값: local-llm-inference)
  LOCAL_LLM_PYTHON_BIN  python 실행 파일 절대경로 지정 시 conda 대신 사용
EOF
}

if [[ $# -lt 1 ]]; then
  usage
  exit 1
fi

MODE="$1"
shift || true

if [[ "$MODE" != "cli" && "$MODE" != "api" ]]; then
  echo "[ERROR] mode는 'cli' 또는 'api'만 가능합니다: $MODE"
  usage
  exit 1
fi

run_with_python_bin() {
  "$PYTHON_BIN" -m src.main "$MODE" "$@"
}

run_with_conda() {
  if ! command -v conda >/dev/null 2>&1; then
    echo "[ERROR] conda 명령을 찾을 수 없습니다."
    echo "        LOCAL_LLM_PYTHON_BIN 환경변수로 python 경로를 지정하세요."
    exit 1
  fi
  conda run -n "$ENV_NAME" python -m src.main "$MODE" "$@"
}

if [[ -n "$PYTHON_BIN" ]]; then
  if [[ ! -x "$PYTHON_BIN" ]]; then
    echo "[ERROR] LOCAL_LLM_PYTHON_BIN 경로가 실행 가능하지 않습니다: $PYTHON_BIN"
    exit 1
  fi
  run_with_python_bin "$@"
else
  run_with_conda "$@"
fi
