"""AI 가위바위보 게임.

사용자가 가위/바위/보 중 하나를 내면 AI가 응답하고, 승패를 판정합니다.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

# ── 환경 설정 ──
ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# ── 입력 매핑 ──
CHOICE_ALIASES: dict[str, str] = {
    "가위": "가위",
    "바위": "바위",
    "보": "보",
    "scissors": "가위",
    "rock": "바위",
    "paper": "보",
    "r": "바위",
    "s": "가위",
    "p": "보",
}

# ── 승패 규칙 ──
# WIN_MAP[a] == b  → a가 b를 이김
WIN_MAP: dict[str, str] = {
    "가위": "보",
    "바위": "가위",
    "보": "바위",
}

SYSTEM_PROMPT = """당신은 가위바위보 게임의 상대입니다.
규칙:
- 반드시 "가위", "바위", "보" 중 하나만 한 단어로 대답하세요.
- 다른 말은 절대 하지 마세요.
"""


def require_api_key() -> None:
    if not API_KEY:
        raise SystemExit(
            "OPENAI_API_KEY가 없습니다. 프로젝트 최상위 .env를 확인하세요."
        )


def parse_choice(raw: str) -> str | None:
    """사용자 입력을 가위/바위/보로 변환. 잘못된 입력이면 None."""
    return CHOICE_ALIASES.get(raw.strip().lower())


def get_ai_choice(client: OpenAI) -> str:
    """OpenAI API를 호출해 AI의 선택을 받아옵니다."""
    response = client.responses.create(
        model=MODEL,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "가위바위보! 하나를 선택하세요."},
        ],
        max_output_tokens=16,
    )
    text = (response.output_text or "").strip()

    # AI 응답에서 가위/바위/보 추출
    for choice in ("가위", "바위", "보"):
        if choice in text:
            return choice

    # 파싱 실패 시 기본값
    return "바위"


def judge(player: str, ai: str) -> str:
    """승패를 판정합니다."""
    if player == ai:
        return "무승부"
    elif WIN_MAP[player] == ai:
        return "승리"
    else:
        return "패배"


def main() -> None:
    require_api_key()
    client = OpenAI(api_key=API_KEY)

    print("=" * 40)
    print("  ✊ ✌️ 🖐️  AI 가위바위보 게임  ✊ ✌️ 🖐️")
    print("=" * 40)
    print("입력: 가위 / 바위 / 보 (또는 r / s / p)")
    print("종료: q 또는 종료\n")

    wins, losses, draws = 0, 0, 0

    while True:
        raw = input("무엇을 내시겠습니까? ").strip()
        if raw.lower() in {"q", "quit", "종료", "exit"}:
            break

        player = parse_choice(raw)
        if player is None:
            print("가위, 바위, 보 중 하나를 입력하세요.\n")
            continue

        try:
            ai = get_ai_choice(client)
        except Exception as exc:
            print(f"API 호출 실패: {exc}")
            return

        result = judge(player, ai)

        # 결과 이모지
        emoji = {"승리": "🎉", "패배": "😢", "무승부": "🤝"}[result]

        print(f"\n  나: {player}  vs  AI: {ai}")
        print(f"  결과: {emoji} {result}!\n")

        if result == "승리":
            wins += 1
        elif result == "패배":
            losses += 1
        else:
            draws += 1

        print(f"  [전적] {wins}승 {losses}패 {draws}무\n")

    print(f"\n게임 종료! 최종 전적: {wins}승 {losses}패 {draws}무")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n중단되었습니다.")
        sys.exit(0)
