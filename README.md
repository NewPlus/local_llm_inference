# local_llm_inference
로컬에서 Ollama + vLLM을 한 번에 띄우고, API/CLI로 바로 추론해볼 수 있는 프로젝트입니다.
- by. Yonghwan.Lee
- 2026.02.28

## News
- [v1.0.0.1] 2026.02.25: Release v1.0.0.1 - 기본 기능 완성 및 배포
- [v0.0.1.1] 2026.02.28: 기본 구조 및 골격 세팅
- [v0.0.0.1] 2026.02.28: 프로젝트 시작

## Quick Start (5분)
### 1) 설치
권장 환경: Python 3.12 (conda 환경명 `local-llm-inference`)

```bash
pip install -r requirements.txt
```

### 2) API 서버 실행
```bash
python -m src.main api
```

실행되면 문서 페이지:
- http://127.0.0.1:18080/docs
- http://127.0.0.1:18080/redoc

### 3) 첫 추론 테스트 (CLI)
```bash
python -m src.main cli infer --model-id qwen-27b-ollama --prompt "안녕" --timeout 300
```

### 4) 예제 스크립트 실행
```bash
python examples/chat_roundtrip.py --base-url http://127.0.0.1:18080 --model-id qwen-27b-ollama --timeout 300
python examples/vllm_roundtrip.py --base-url http://127.0.0.1:18080 --model-id qwen-27b-vllm --timeout 300
```

## 무엇을 할 수 있나요?
- 엔진 제어: `ollama`, `vllm` 시작/중지/상태 확인
- 모델 제어: 목록/로드/언로드/정책 반영(`apply`)
- 추론: CLI 또는 REST API(`/inference`)로 요청

## 자주 쓰는 명령어
### 엔진 시작/상태
```bash
python -m src.main cli start
python -m src.main cli health
python -m src.main cli status
```

### 모델 확인/정책 반영
```bash
python -m src.main cli models
python -m src.main cli apply
python -m src.main cli down
```

### 추론
```bash
python -m src.main cli infer --model-id qwen-27b-ollama --prompt "한 줄로 소개해줘" --max-tokens 200 --timeout 300
python -m src.main cli infer --model-id qwen-27b-vllm --prompt "한 줄 요약해줘" --max-tokens 128 --timeout 300
```

## API 빠른 확인
서버 실행 후:
- 문서: http://127.0.0.1:18080/docs
- 헬스체크: `GET /health`
- 추론: `POST /inference`

포트 변경:
```bash
LOCAL_LLM_API_PORT=19090 python -m src.main api
```

## 설정 파일
모든 모델/엔진 설정은 `config/models.yml`에서 관리합니다.

현재 기본 모델 ID:
- Ollama: `qwen-27b-ollama` (`qwen3:32b`)
- vLLM: `qwen-27b-vllm` (`Qwen/Qwen3-8B`)

## 문제 해결
- 포트 충돌: `LOCAL_LLM_API_PORT`로 포트 변경
- timeout 발생: `--timeout` 증가, `--max-tokens` 조정
- 설정 변경 후 미반영: API 재시작

## 프로젝트 구조 (간단)
```text
examples/   실행 예제 스크립트
config/     모델/엔진 설정(YAML)
src/        실제 애플리케이션 코드
scripts/    실행 보조 스크립트
```
