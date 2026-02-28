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


def _ns_to_sec(value: int | None) -> float | None:
    if value is None:
        return None
    return round(value / 1_000_000_000, 3)


def _print_health_summary(health: dict) -> None:
    ollama_ok = health.get("ollama", {}).get("ok")
    vllm_ok = health.get("vllm", {}).get("ok")
    model_count = len(health.get("ollama", {}).get("payload", {}).get("models", []))
    print("[HEALTH]")
    print(f"- ollama: {'ok' if ollama_ok else 'fail'} (models={model_count})")
    print(f"- vllm: {'ok' if vllm_ok else 'fail'}")


def _print_inference_summary(result: dict) -> None:
    output = result.get("output") or {}
    readable = _extract_readable_text(output.get("response", ""))

    print("\n[SUMMARY]")
    print(f"- ok: {result.get('ok')}")
    print(f"- model_id: {result.get('model_id')}")
    print(f"- engine: {result.get('engine')}")
    print(f"- model: {output.get('model')}")
    print(f"- done_reason: {output.get('done_reason')}")
    print(f"- prompt_tokens: {output.get('prompt_eval_count')}")
    print(f"- generated_tokens: {output.get('eval_count')}")

    total_sec = _ns_to_sec(output.get("total_duration"))
    eval_sec = _ns_to_sec(output.get("eval_duration"))
    if total_sec is not None:
        print(f"- total_time_sec: {total_sec}")
    if eval_sec is not None:
        print(f"- generation_time_sec: {eval_sec}")

    print("\n[ANSWER]")
    if readable:
        print(readable)
    else:
        print("가시적 답변 없이 사고 토큰만 생성되었습니다. `--max-tokens`를 늘리거나 프롬프트에 '생각 과정 없이 최종 답만 한 줄로 답해'를 추가해 다시 시도하세요.")


def main() -> None:
    parser = argparse.ArgumentParser(description="로컬 LLM API 간단 왕복 예제")
    parser.add_argument("--base-url", default="http://127.0.0.1:18080", help="로컬 API 서버 주소")
    parser.add_argument("--model-id", default="qwen-27b-ollama", help="사용할 모델 ID")
    parser.add_argument("--prompt", default="안녕! 너는 누구니?", help="질문 프롬프트")
    parser.add_argument("--max-tokens", type=int, default=200, help="최대 생성 토큰 수")
    parser.add_argument("--timeout", type=int, default=300, help="HTTP 요청 타임아웃(초)")
    parser.add_argument("--raw", action="store_true", help="원본 JSON 응답까지 출력")
    args = parser.parse_args()

    health_url = f"{args.base_url}/health"
    inference_url = f"{args.base_url}/inference"

    try:
        health = _request_json("GET", health_url, timeout=args.timeout)
        _print_health_summary(health)

        payload = {
            "model_id": args.model_id,
            "prompt": args.prompt,
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": args.max_tokens,
            "timeout": args.timeout,
        }
        result = _request_json("POST", inference_url, payload, timeout=args.timeout)

        print("\n[REQUEST]")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        _print_inference_summary(result)

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
