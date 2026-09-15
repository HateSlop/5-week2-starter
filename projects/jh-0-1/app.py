import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env")

API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

SYSTEM_PROMPT = (
    "너는 따뜻하고 다정한 고민 상담 친구야. 사용자가 털어놓는 고민을 듣고, "
    "짧고 진심 어린 위로와 실천 가능한 조언을 한두 문장으로 건네줘. "
    "판단하거나 훈계하지 말고, 공감하는 말투를 유지해."
)


def ask_openai(client: OpenAI, history: list[dict]) -> str:
    response = client.responses.create(
        model=MODEL,
        instructions=SYSTEM_PROMPT,
        input=history,
        max_output_tokens=200,
    )
    return response.output_text.strip()


def main() -> None:
    if not API_KEY:
        raise SystemExit(
            "OPENAI_API_KEY가 없습니다. 프로젝트 최상위 .env 파일을 확인하세요."
        )

    client = OpenAI(api_key=API_KEY)
    history: list[dict] = []

    print("=== 고민 상담 봇 ===")
    print("오늘 있었던 고민을 편하게 적어 주세요. 종료하려면 'exit'를 입력하세요.\n")

    while True:
        user_input = input("나: ").strip()

        if not user_input:
            print("(입력이 비어 있어요. 다시 입력해 주세요.)\n")
            continue

        if user_input.lower() in {"exit", "quit", "종료"}:
            print("상담 봇: 오늘도 고생 많았어요. 다음에 또 이야기해요.")
            break

        history.append({"role": "user", "content": user_input})

        try:
            reply = ask_openai(client, history)
        except Exception as error:
            print(f"(오류가 발생했습니다: {error})\n")
            history.pop()
            continue

        print(f"상담 봇: {reply}\n")
        history.append({"role": "assistant", "content": reply})


if __name__ == "__main__":
    main()
