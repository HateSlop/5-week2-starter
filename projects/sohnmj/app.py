import os
import sys
from dotenv import load_dotenv
from openai import OpenAI


def main() -> None:
    # 프로젝트 루트의 .env 파일 로드
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    if not api_key:
        print("오류: OPENAI_API_KEY가 없습니다. 루트 .env 파일을 확인하세요.")
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    instructions = (
        "당신은 배틀그라운드(PUBG) 이스포츠 전문 AI 어시스턴트입니다.\n"
        "국내 대회(PWS) 및 글로벌 대회(PGS, PNC, PGC 등)의 경기 일정, 진행 방식, 결과 브리핑, 주요 소식을 안내합니다.\n"
        "사용자의 질문에 맞춰 핵심 정보를 200토큰 이내로 명확하고 간결하게 답변하세요."
    )

    print("=" * 60)
    print("  PUBG 이스포츠 안내 AI (PWS, PGS, PNC, PGC 일정/결과)")
    print("=" * 60)
    print("대화를 종료하려면 'q' 또는 '종료'를 입력하세요.\n")

    while True:
        try:
            user_input = input("[질문 입력] > ").strip().lstrip("\ufeff")
        except (KeyboardInterrupt, EOFError):
            print("\n프로그램을 종료합니다.")
            break

        if not user_input:
            print("입력이 비어 있습니다. 질문을 입력해 주세요.")
            continue

        if user_input.lower() in ("q", "quit", "exit", "종료"):
            print("이용해 주셔서 감사합니다. 대화를 종료합니다.")
            break

        print("\nAI가 답변을 확인 중입니다...")

        try:
            response = client.responses.create(
                model=model,
                instructions=instructions,
                input=user_input,
                max_output_tokens=200,
            )
            print("\n[AI 응답]")
            print(response.output_text)
            print("-" * 60)
        except Exception as error:
            print(f"\n요청 처리 중 오류가 발생했습니다: {type(error).__name__}")
            print("-" * 60)


if __name__ == "__main__":
    main()
