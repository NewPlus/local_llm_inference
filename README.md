# local_llm_inference
Code repo for local LLM inference system

## Quick Start

### 1) Python 환경
- conda 환경: `local-llm-inference` (Python 3.12)
- 의존성 설치:

```bash
pip install -r requirements.txt
```

### 2) 설정 파일
- 기본 설정 파일: `config/models.yml`
- 테스트 모델 기본값:
	- Ollama: `qwen3.5:27b`
	- vLLM: `qwen3.5:27b`

### 3) CLI 실행

```bash
python -m src.main cli start
python -m src.main cli health
python -m src.main cli models
python -m src.main cli infer --model-id qwen-27b-ollama --prompt "안녕"
```

엔진 미지정 시 기본 정책으로 `ollama` + `vllm` 동시 기동을 시도합니다.

### 4) API 실행

```bash
python -m src.main api
```

서버 시작 시 터미널에 아래 API 문서 URL이 출력됩니다.
- `http://127.0.0.1:18080/docs`
- `http://127.0.0.1:18080/redoc`
- `http://127.0.0.1:18080/openapi.json`

기본 포트(18080)를 바꾸려면 아래처럼 실행합니다.

```bash
LOCAL_LLM_API_PORT=19090 python -m src.main api
```
