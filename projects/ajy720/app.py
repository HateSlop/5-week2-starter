"""OpenAI와 짧게 대결하는 터미널 요트 다이스 프로토타입."""

from __future__ import annotations

import random
import re
import sys
from collections import Counter
from pathlib import Path

from dotenv import dotenv_values
from openai import OpenAI


ROOT = Path(__file__).resolve().parents[2]
CONFIG = dotenv_values(ROOT / ".env")
API_KEY = CONFIG.get("OPENAI_API_KEY")
MODEL = CONFIG.get("OPENAI_MODEL") or "gpt-4o-mini"

CATEGORIES = (
    "ones", "twos", "threes", "fours", "fives", "sixes",
    "choice", "four_kind", "full_house", "small_straight",
    "large_straight", "yacht",
)
LABELS = {
    "ones": "에이스", "twos": "듀스", "threes": "트리플", "fours": "쿼드",
    "fives": "펜타", "sixes": "헥사", "choice": "초이스", "four_kind": "포카드",
    "full_house": "풀하우스", "small_straight": "스몰 스트레이트",
    "large_straight": "라지 스트레이트", "yacht": "요트",
}
class GameExit(Exception):
    """사용자가 게임을 끝내고 싶을 때 사용한다."""


def roll(indices: list[int] | None = None, dice: list[int] | None = None) -> list[int]:
    """새 주사위 또는 선택한 위치만 다시 굴린 주사위를 반환한다."""
    if dice is None:
        return [random.randint(1, 6) for _ in range(5)]
    for index in indices or []:
        dice[index] = random.randint(1, 6)
    return dice


def score(dice: list[int], category: str) -> int:
    counts = Counter(dice)
    total = sum(dice)
    number_categories = {"ones": 1, "twos": 2, "threes": 3, "fours": 4, "fives": 5, "sixes": 6}
    if category in number_categories:
        value = number_categories[category]
        return value * counts[value]
    if category == "choice":
        return total
    if category == "four_kind":
        return total if max(counts.values()) >= 4 else 0
    if category == "full_house":
        return total if sorted(counts.values()) in ([2, 3], [5]) else 0
    unique = set(dice)
    if category == "small_straight":
        return 15 if any(run <= unique for run in ({1, 2, 3, 4}, {2, 3, 4, 5}, {3, 4, 5, 6})) else 0
    if category == "large_straight":
        return 30 if unique in ({1, 2, 3, 4, 5}, {2, 3, 4, 5, 6}) else 0
    return 50 if len(counts) == 1 else 0


def available_text(categories: set[str]) -> str:
    return ", ".join(f"{key}({LABELS[key]})" for key in CATEGORIES if key in categories)


def clear_screen() -> None:
    if sys.stdout.isatty():
        print("\033[2J\033[H", end="")


def show_progress(available: set[str], card_scores: dict[str, int]) -> None:
    earned = " · ".join(f"{LABELS[card]} {points}점" for card, points in card_scores.items()) or "아직 기록한 카드 없음"
    remaining = ", ".join(LABELS[card] for card in CATEGORIES if card in available)
    print(f"기록 완료 ({len(card_scores)}/12): {earned}")
    print(f"남은 카드 ({len(available)}장): {remaining}")


def show_status(round_number: int, human_total: int, ai_total: int, available: set[str]) -> None:
    print("=" * 62)
    print(f"요트 다이스 · AI 대결  |  ROUND {round_number:02}/12")
    print(f"내 점수 {human_total}점  /  AI 점수 {ai_total}점  /  남은 카드 {len(available)}장")
    print("=" * 62)


def show_dice(dice: list[int], available: set[str], card_scores: dict[str, int]) -> None:
    positions = "  ".join(f"[{index}]" for index in range(1, 6))
    values = "  ".join(f" {value} " for value in dice)
    print(f"\n내 주사위\n{positions}\n{values}")
    print()
    show_progress(available, card_scores)


def show_scorecard(available: set[str], card_scores: dict[str, int], dice: list[int]) -> None:
    print("\n점수표 · 번호 또는 영문 카테고리를 입력하세요")
    for number, category in enumerate(CATEGORIES, 1):
        if category in card_scores:
            print(f"[{number:02}] {LABELS[category]} — 기록: {card_scores[category]}점")
        else:
            print(f"[{number:02}] {LABELS[category]} — 이번 주사위: {score(dice, category)}점")


def pause(message: str) -> None:
    if input(message).strip().lower() in {"q", "quit", "종료"}:
        raise GameExit


def ai_turn(client: OpenAI, used: set[str], human_score: int, ai_score: int) -> tuple[str, list[int], str]:
    dice = roll()
    choices = set(CATEGORIES) - used
    candidate_scores = ", ".join(f"{category}={score(dice, category)}" for category in sorted(choices))
    prompt = f"""너는 요트 다이스 게임의 친근하지만 승부욕 있는 AI 상대다.
AI 주사위는 {dice}이고, 아직 쓸 수 있는 카테고리는 {available_text(choices)}다.
사람 점수는 {human_score}, AI 점수는 {ai_score}이다.
현재 가능한 카테고리별 점수는 {candidate_scores}다. 가장 높은 점수의 카테고리를 골라라.
반드시 첫 줄을 'CHOICE: 영문카테고리' 형식으로 쓰고, 가능한 카테고리 하나만 고르라.
둘째 줄에는 한국어로 1~2문장의 짧은 승부 멘트와 선택 이유를 써라.
카테고리 목록: {', '.join(sorted(choices))}"""
    response = client.responses.create(
        model=MODEL,
        input=prompt,
        max_output_tokens=200,
    )
    text = response.output_text.strip()
    match = re.search(r"^CHOICE:\s*([a-z_]+)", text, re.MULTILINE)
    choice = match.group(1) if match and match.group(1) in choices else max(choices, key=lambda item: score(dice, item))
    message = re.sub(r"^CHOICE:.*\n?", "", text, count=1, flags=re.MULTILINE).strip()
    return choice, dice, message or "AI가 조용히 점수를 기록했습니다."


def choose_reroll(dice: list[int], available: set[str], card_scores: dict[str, int]) -> list[int]:
    rerolls_left = 2
    while rerolls_left:
        raw = input(f"\n  다시 굴릴 위치 (예: 1 3 5 / Enter=점수 선택 / q=종료)  ·  {rerolls_left}회 남음 > ").strip()
        if not raw or raw.lower() in {"s", "score", "점수"}:
            return dice
        if raw.lower() in {"q", "quit", "종료"}:
            raise GameExit
        try:
            positions = sorted({int(value) - 1 for value in re.split(r"[\s,]+", raw) if value})
            if not positions or any(position not in range(5) for position in positions):
                raise ValueError
        except ValueError:
            print(f"  ⚠ 1~5 사이 위치만 입력해 주세요. 기회는 그대로 {rerolls_left}회 남았습니다.")
            continue
        roll(positions, dice)
        rerolls_left -= 1
        show_dice(dice, available, card_scores)
        print(f"✓ 다시 굴렸습니다. 남은 기회: {rerolls_left}회")
    print("\n  재굴림 기회를 모두 사용했습니다. 점수표를 고르세요.")
    return dice


def choose_category(available: set[str], card_scores: dict[str, int], dice: list[int]) -> str:
    while True:
        show_scorecard(available, card_scores, dice)
        raw = input("\n  기록할 카드 > ").strip().lower()
        if raw in {"q", "quit", "종료"}:
            raise GameExit
        category = CATEGORIES[int(raw) - 1] if raw.isdigit() and 1 <= int(raw) <= len(CATEGORIES) else raw
        if category in available:
            print(f"\n  ✓ {LABELS[category]}에 {score(dice, category)}점을 기록했습니다.")
            return category
        print("  ⚠ 아직 사용하지 않은 카드의 번호 또는 영문 카테고리를 입력해 주세요.")


def main() -> None:
    if not API_KEY:
        print("프로젝트 최상위 .env에 OpenAI API 설정이 필요합니다. 키 값은 화면에 표시하지 않습니다.")
        return
    client = OpenAI(api_key=API_KEY)
    human_available, ai_used = set(CATEGORIES), set()
    human_scores: dict[str, int] = {}
    human_total = ai_total = 0
    clear_screen()
    print("\n  AI와 12장의 요트 다이스 카드를 먼저 채워 보세요.")
    pause("  Enter를 누르면 시작합니다. (q=언제든 종료) ")
    for round_number in range(1, 13):
        clear_screen()
        show_status(round_number, human_total, ai_total, human_available)
        human_dice = roll()
        show_dice(human_dice, human_available, human_scores)
        print("\n최대 두 번, 원하는 주사위만 다시 굴릴 수 있습니다.")
        choose_reroll(human_dice, human_available, human_scores)
        category = choose_category(human_available, human_scores, human_dice)
        human_available.remove(category)
        points = score(human_dice, category)
        human_scores[category] = points
        human_total += points
        print("\nAI가 주사위와 점수표를 살피는 중...")
        try:
            ai_category, ai_dice, ai_message = ai_turn(client, ai_used, human_total, ai_total)
        except Exception as error:
            print(f"AI 응답을 받지 못해 게임을 멈춥니다: {type(error).__name__}")
            return
        ai_used.add(ai_category)
        ai_points = score(ai_dice, ai_category)
        ai_total += ai_points
        print(f"\nAI 주사위: {ai_dice}")
        print(f"AI 기록: {LABELS[ai_category]} {ai_points}점")
        print(f"AI: {ai_message}")
        print(f"\n현재 점수: 내 점수 {human_total}점 / AI 점수 {ai_total}점")
        pause("\nEnter를 누르면 다음 라운드로 갑니다. (q=종료) ")
    result = "승리" if human_total > ai_total else "패배" if human_total < ai_total else "무승부"
    print(f"\n최종 점수 | 나 {human_total} : AI {ai_total} — {result}!")


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt, GameExit):
        print("\n게임을 종료합니다.")
