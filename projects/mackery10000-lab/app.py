import os
import random
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

if not api_key:
    raise SystemExit("OPENAI_API_KEY가 없습니다. 최상위 .env 파일을 확인하세요.")

client = OpenAI(api_key=api_key)

WORDS = {
    "하": ["사과", "고양이", "강아지", "비행기", "피자", "축구공", "냉장고", "자전거", "호랑이", "스마트폰"],
    "중": ["나침반", "잠수함", "피아노", "선인장", "망원경", "에스프레소", "현미경", "낙하산", "선풍기"],
    "상": ["신기루", "타임캡슐", "미토콘드리아", "블랙홀", "페로몬", "카멜레온", "판토마임", "인공위성"],
}


def call_ai(instructions: str, prompt: str) -> str:
    response = client.responses.create(
        model=model,
        instructions=instructions,
        input=prompt,
        max_output_tokens=150,
    )
    return response.output_text.strip()


def play_mode_ai_guess(diff: str) -> None:
    print(f"\n[AI가 맞히기 모드 - 난이도: {diff}]")
    print("사용자님은 하나의 단어를 마음속으로 정해주세요.")
    user_word = input("단어를 미리 적어두려면 입력(생략 시 엔터): ").strip()
    ready = input("준비를 마치셨으면 엔터를 눌러 AI의 첫 질문을 받아보세요: ")

    diff_rules = {
        "하": "핵심적인 질문을 빠르게 선택하여 높은 추론 능력으로 빠르게 정답을 맞히세요.",
        "중": "일반적인 수준의 질문과 추론을 사용하여 단계적으로 범위를 좁히세요.",
        "상": "우회적이거나 제한된 정보를 활용하여 조심스럽게 추리하세요.",
    }
    instructions = (
        "당신은 스무고개 게임에서 정답을 맞히는 도전자 AI입니다.\n"
        f"난이도 규칙: {diff_rules.get(diff, diff_rules['중'])}\n"
        "규칙:\n"
        "1. 질문은 한 번에 단 하나만 짧고 명확하게 하세요.\n"
        "2. 정답을 확신할 때는 '정답은 [단어]인가요?' 형태로 추측을 제시하세요.\n"
        "3. 이전 질문과 답변 내역을 바탕으로 중복 없이 논리적으로 질문하세요."
    )

    history: list[str] = []
    first_prompt = "게임을 시작합니다. 범위를 좁힐 수 있는 첫 번째 질문을 해주세요."
    current_ai_q = call_ai(instructions, first_prompt)

    for q_num in range(1, 21):
        print(f"\n[질문 {q_num}/20] AI: {current_ai_q}")
        ans = input("답변 (네/아니오/정답 등, 종료: q): ").strip()
        if not ans:
            ans = "잘 모르겠습니다."
        if ans.lower() == "q":
            print("게임을 중단했습니다.")
            return

        if "정답" in ans or (user_word and user_word in current_ai_q and "인가요" in current_ai_q):
            print(f"\n🎉 AI가 {q_num}번째 질문만에 정답을 맞혔습니다! (AI 승리)")
            return

        if q_num == 20:
            print("\n20개의 질문을 모두 사용했습니다. 사용자의 승리입니다!")
            if user_word:
                print(f"정답 단어: {user_word}")
            return

        history.append(f"AI 질문: {current_ai_q} -> 사용자 답변: {ans}")
        history_text = "\n".join(history)
        next_prompt = (
            f"지금까지의 대화 기록:\n{history_text}\n\n"
            f"위 답변들을 바탕으로, 다음 {q_num + 1}번째 질문 또는 정답 추측을 하나만 제시하세요."
        )
        current_ai_q = call_ai(instructions, next_prompt)


def play_mode_user_guess(diff: str) -> None:
    secret_word = random.choice(WORDS.get(diff, WORDS["중"]))
    print(f"\n[사용자가 맞히기 모드 - 난이도: {diff}]")
    print("AI가 비밀 단어를 하나 선택했습니다. 20번 안에 질문하여 맞혀보세요!")
    print("팁: '네 / 아니오'로 답할 수 있는 질문을 하거나, '정답: [단어]'를 입력하세요.")

    hint_guide = (
        "답변에 충분한 정보를 제공하고 친절하게 안내하세요."
        if diff == "하"
        else "정답을 직접 드러내지 말고 최소한의 정보만 제공하세요."
    )
    instructions = (
        f"당신은 스무고개 게임의 출제자 AI입니다. 비밀 단어는 '{secret_word}'입니다.\n"
        f"난이도 지침: {hint_guide}\n"
        "규칙:\n"
        "1. 절대로 비밀 단어 자체를 직접 발설하지 마세요.\n"
        "2. 사용자의 질문에 사실에 기반하여 짧게 답하세요 (예: '네.', '아니요.', '경우에 따라 다릅니다.', '관련 없습니다.').\n"
        "3. 사용자가 비밀 단어를 정확히 맞히면 반드시 '정답입니다!'라고 답변하세요."
    )

    history: list[str] = []

    for q_num in range(1, 21):
        user_q = input(f"\n[질문 {q_num}/20] 질문 입력 (종료: q): ").strip()
        if not user_q:
            print("질문을 입력해주세요.")
            continue
        if user_q.lower() == "q":
            print(f"게임을 중단했습니다. 비밀 단어는 '{secret_word}'였습니다.")
            return

        history_text = "\n".join(history) if history else "없음"
        prompt = (
            f"대화 기록:\n{history_text}\n\n"
            f"사용자 질문: {user_q}\n"
            f"비밀 단어('{secret_word}')를 바탕으로 답변하세요:"
        )

        ai_ans = call_ai(instructions, prompt)
        print(f"AI: {ai_ans}")
        history.append(f"사용자: {user_q} -> AI: {ai_ans}")

        clean_user_q = user_q.replace(" ", "")
        clean_secret = secret_word.replace(" ", "")
        if "정답입니다" in ai_ans or clean_secret in clean_user_q:
            print(f"\n🎉 정답입니다! {q_num}번째 질문만에 맞히셨습니다! (사용자 승리)")
            print(f"비밀 단어: {secret_word}")
            return

    print(f"\n20개의 질문을 모두 소진했습니다. 실패하셨습니다! (AI 승리)")
    print(f"비밀 단어는 '{secret_word}'였습니다.")


def main() -> None:
    print("=" * 45)
    print("       🤖 스무고개 미니게임 AI 🎮")
    print("=" * 45)

    diff_map = {"1": "하", "2": "중", "3": "상"}

    while True:
        print("\n[게임 모드 선택]")
        print("1. AI가 맞히기 (사용자가 생각한 단어를 AI가 추리)")
        print("2. 사용자가 맞히기 (AI가 정한 단어를 사용자가 추리)")
        print("q. 종료")
        mode = input("선택 (1/2/q): ").strip().lower()

        if mode == "q":
            print("게임을 종료합니다. 이용해 주셔서 감사합니다!")
            break
        if mode not in ("1", "2"):
            print("1, 2, q 중 하나를 입력해주세요.")
            continue

        print("\n[난이도 선택]")
        print("1. 하  2. 중  3. 상")
        diff_choice = input("난이도 선택 (1/2/3, 기본값 2): ").strip()
        diff = diff_map.get(diff_choice, "중")

        if mode == "1":
            play_mode_ai_guess(diff)
        else:
            play_mode_user_guess(diff)

        replay = input("\n다시 플레이하시겠습니까? (y/n): ").strip().lower()
        if replay != "y":
            print("게임을 종료합니다. 이용해 주셔서 감사합니다!")
            break


if __name__ == "__main__":
    main()

