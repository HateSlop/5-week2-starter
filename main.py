import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

if not api_key:
    raise SystemExit(
        "OPENAI_API_KEY가 없습니다. 프로젝트의 .env 파일을 확인하세요."
    )

question = input("AI에게 물어볼 내용을 입력하세요: ").strip()
if not question:
    raise SystemExit("입력이 비어 있어 API를 호출하지 않았습니다.")

client = OpenAI(api_key=api_key)
response = client.responses.create(
    model=model,
    input=question,
    max_output_tokens=150,
)

print("\nAI 응답:")
print(response.output_text)
