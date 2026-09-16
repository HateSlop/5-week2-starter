import os
import sys

from dotenv import load_dotenv
from openai import OpenAI


def get_user_input() -> str:
    print("=" * 45)
    print("        HSK 맞춤형 학습 플래너 (AI)")
    print("=" * 45)

    target_level = input("\n1. 목표 HSK 급수를 입력하세요 (예: 4급, 5급): ").strip()
    if not target_level:
        print("목표 급수가 입력되지 않았습니다.")
        sys.exit(1)

    target_period = input("2. 목표 취득 시기 또는 준비 기간을 입력하세요 (예: 2개월 뒤, 100일): ").strip()
    if not target_period:
        print("취득 시기가 입력되지 않았습니다.")
        sys.exit(1)

    current_level = input("3. 현재 중국어 실력/경험을 입력하세요 (선택 사항, 엔터 시 건너뜀): ").strip()
    if not current_level:
        current_level = "기초 없음 또는 미입력"

    prompt = (
        "당신은 HSK 전문 학습 컨설턴트입니다. "
        "사용자의 목표에 맞춘 학습 플랜을 제안하세요.\n\n"
        f"[사용자 정보]\n"
        f"- 목표 급수: {target_level}\n"
        f"- 준비 기간: {target_period}\n"
        f"- 현재 실력: {current_level}\n\n"
        "[작성 규칙]\n"
        "1. 서론과 결론 인사말을 생략하고, 다음 3단계만 바로 출력하세요.\n"
        "   - 1단계(어휘/기초): 핵심 행동 1문장\n"
        "   - 2단계(영역별 문풀): 핵심 행동 1문장\n"
        "   - 3단계(실전 모의고사): 핵심 행동 1문장\n"
        "2. 반드시 한국어로 각 항목을 40자 이내의 완결된 문장으로 작성하세요."
    )
    return prompt


def main() -> None:
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    if not api_key:
        print("오류: OPENAI_API_KEY가 설정되지 않았습니다.")
        print("프로젝트 루트의 .env 파일에 OPENAI_API_KEY를 설정해 주세요.")
        sys.exit(1)

    prompt = get_user_input()

    print("\nAI 학습 플랜을 생성 중입니다...")
    try:
        client = OpenAI(api_key=api_key)
        response = client.responses.create(
            model=model,
            input=prompt,
            max_output_tokens=200,
        )
        print("\n" + "=" * 45)
        print("            추천 학습 플랜")
        print("=" * 45)
        print(response.output_text)
        print("=" * 45)
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
