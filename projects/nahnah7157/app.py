import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

if not api_key:
    raise SystemExit("OPENAI_API_KEY가 없습니다. .env 파일을 확인하세요.")

client = OpenAI(api_key=api_key)

# 참고문헌이 담긴 파일 읽기
file_path = "projects/nahnah7157/references.txt"  # 본인 경로에 맞게 수정

try:
    with open(file_path, "r", encoding="utf-8") as f:
        raw_text = f.read()
except FileNotFoundError:
    raise SystemExit(f"{file_path} 파일을 찾을 수 없습니다. 파일을 만들어 주세요.")

if not raw_text.strip():
    raise SystemExit("참고문헌 파일 내용이 비어 있습니다.")

prompt = f"""
너는 학술 논문 참고문헌 서식 전문가야. 아래에 입력된 여러 개의 참고문헌 원문을 각각 'APA 7판(APA Style 7th edition)' 양식에 정확히 맞춰서 순서대로 교정해줘.
부가 설명은 제외하고, 교정된 참고문헌 목록만 깔끔하게 출력해줘.

참고문헌 원문:
{raw_text}
"""

response = client.chat.completions.create(
    model=model,
    messages=[{"role": "user", "content": prompt}]
)

print("\n[APA 교정 결과]")
print(response.choices[0].message.content)
