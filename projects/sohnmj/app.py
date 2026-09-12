import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


# 프로젝트 최상위 .env 파일 로드
root_env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=root_env_path, override=True)

api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

if not api_key:
    raise SystemExit(
        "OPENAI_API_KEY가 없습니다. 프로젝트 최상위의 .env 파일을 확인하세요."
    )

print("=== 배틀그라운드(PUBG) e스포츠 대회 일정 안내 도우미 ===")
print("궁금한 배그 대회 일정이나 현재 진행 중인 경기 일정을 물어보세요.")
question = input("\n질문 입력: ").strip()

if not question:
    raise SystemExit("입력이 비어 있어 API를 호출하지 않았습니다.")

client = OpenAI(api_key=api_key)

instructions = (
    "당신은 배틀그라운드(PUBG) e스포츠 대회 일정 안내 도우미입니다. "
    "사용자가 묻는 배틀그라운드 대회(PWS, PGS, PGC 등) 일정을 친절하게 안내하세요. "
    "만약 진행 중인 대회나 예정된 일정이 없다면 반드시 일정이 없다고 솔직하게 알려주세요."
)
try:
    response = client.responses.create(
        model=model,
        instructions=instructions,
        input=question,
        max_output_tokens=180,
    )
    print("\n[AI 응답]")
    print(response.output_text)
except Exception as e:
    import traceback
    print("\n--- [실제 발생한 에러 상세 내용] ---")
    traceback.print_exc()
    print("------------------------------------\n")
    raise SystemExit(
        "OpenAI API 호출에 실패했습니다. 최상위 .env의 OPENAI_API_KEY와 설정을 확인해 주세요."
    )
