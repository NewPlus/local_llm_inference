from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ApiDocsPublisher:
    """API 문서 경로를 터미널에 출력하는 퍼블리셔."""

    docs_paths: list[str]

    def publish(self, host: str, port: int) -> None:
        """호스트/포트를 기준으로 문서 URL 목록을 출력한다."""
        base = f"http://{host}:{port}"
        print("[API DOCS] 접근 가능한 문서 경로")
        for path in self.docs_paths:
            print(f"- {base}{path}")
