from __future__ import annotations

import argparse
import json
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def _request_json(method: str, url: str, payload: dict | None = None, timeout: int = 120) -> dict:
    data = None
    headers = {"Content-Type": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")

    request = Request(url=url, data=data, method=method, headers=headers)
    with urlopen(request, timeout=timeout) as response:
        body = response.read().decode("utf-8")
        return json.loads(body) if body else {}


def _extract_readable_text(raw_text: str) -> str:
    text = raw_text or ""
    if "<think>" in text and "</think>" not in text:
        return ""
    if "</think>" in text:
        text = text.split("</think>", 1)[1]
    text = re.sub(r"<think>.*", "", text, flags=re.DOTALL)
    return text.strip() or raw_text.strip()


def _extract_answer_from_output(output: dict) -> str:
    ollama_text = output.get("response")
    if isinstance(ollama_text, str) and ollama_text.strip():
        return _extract_readable_text(ollama_text)

    choices = output.get("choices")
    if isinstance(choices, list) and choices:
        message = (choices[0] or {}).get("message") or {}
        content = message.get("content")
        if isinstance(content, str) and content.strip():
            return _extract_readable_text(content)

    return ""


def main() -> None:
    parser = argparse.ArgumentParser(description="vLLM 모델 간단 추론 예제")
    parser.add_argument("--base-url", default="http://127.0.0.1:18080", help="로컬 API 서버 주소")
    parser.add_argument("--model-id", default="qwen-27b-vllm", help="vLLM 모델 ID")
    parser.add_argument("--prompt", default="안녕! 한 줄로 자기소개해줘.", help="질문 프롬프트")
    parser.add_argument("--max-tokens", type=int, default=2048, help="최대 생성 토큰 수")
    parser.add_argument("--timeout", type=int, default=300, help="HTTP 요청 타임아웃(초)")
    parser.add_argument("--raw", action="store_true", help="원본 JSON 응답까지 출력")
    args = parser.parse_args()

    try:
        health = _request_json("GET", f"{args.base_url}/health", timeout=args.timeout)
        vllm_ok = health.get("vllm", {}).get("ok")
        print("[HEALTH]")
        print(f"- vllm: {'ok' if vllm_ok else 'fail'}")

        payload = {
            "model_id": args.model_id,
            "prompt": (
                f"{args.prompt}\n\n"
                "규칙: 사고 과정(<think>)을 출력하지 말고, 최종 답변만 한국어 한 줄로 답하세요."
            ),
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": args.max_tokens,
            "timeout": args.timeout,
        }
        result = _request_json("POST", f"{args.base_url}/inference", payload, timeout=args.timeout)

        print("\n[REQUEST]")
        print(json.dumps(payload, ensure_ascii=False, indent=2))

        print("\n[SUMMARY]")
        print(f"- ok: {result.get('ok')}")
        print(f"- model_id: {result.get('model_id')}")
        print(f"- engine: {result.get('engine')}")

        output = result.get("output") or {}
        answer = _extract_answer_from_output(output)

        print("\n[ANSWER]")
        if answer:
            print(answer)
        else:
            print("가시적 답변이 비어 있습니다. `--max-tokens`를 늘려 다시 시도하세요.")

        if args.raw:
            print("\n[RESPONSE_RAW]")
            print(json.dumps(result, ensure_ascii=False, indent=2))

        if result.get("ok") is False:
            raise RuntimeError(f"추론 실패: {result.get('error')}")

    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        print(f"HTTP 오류: {exc.code} {exc.reason}\n{body}")
        raise
    except URLError as exc:
        print(f"연결 오류: {exc.reason}")
        print("힌트: 먼저 `python -m src.main api`로 API 서버를 실행하세요.")
        raise


if __name__ == "__main__":
    main()
