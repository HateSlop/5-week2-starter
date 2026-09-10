import os
import sys
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# Load .env from project root (two levels up from this file)
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(env_path)

api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

if not api_key:
    print("Error: OPENAI_API_KEY not found in .env")
    sys.exit(1)

client = OpenAI(api_key=api_key)

SYSTEM_PROMPT = (
    "You are a friendly Japanese language tutor for Korean speakers. "
    "The user is a Korean speaker learning Japanese. "
    "Respond in Korean. Keep explanations short and practical. "
    "Maximum 200 tokens per response."
)


def chat():
    print("=" * 50)
    print("🇯🇵  일본어 학습 도우미 (Japanese Learning Assistant)")
    print("=" * 50)
    print("명령어: quit / exit → 종료")
    print()

    greeting = (
        "안녕하세요! 오늘의 일본어 공부를 시작할까요?\n"
        "모르는 단어나 문장을 입력하거나, '오늘의 표현'이라고 입력해 보세요."
    )
    print(f"💬 {greeting}\n")

    while True:
        try:
            user_input = input("🇰🇷 You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit"):
            print("👋  またね! 또 봐요!")
            break

        try:
            response = client.responses.create(
                model=model,
                instructions=SYSTEM_PROMPT,
                input=user_input,
                max_output_tokens=200,
                temperature=0.7,
            )
            reply = response.output_text.strip()
            print(f"💬 {reply}\n")
        except Exception as e:
            print(f"⚠️  오류: {e}\n")


if __name__ == "__main__":
    chat()