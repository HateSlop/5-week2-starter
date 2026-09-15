import os
from dotenv import load_dotenv
from openai import OpenAI

# 1. 최상위 .env 파일에서 환경변수 로드
load_dotenv()

# 2. OpenAI API 키 및 모델 설정
api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

if not api_key:
    raise SystemExit(
        "OPENAI_API_KEY가 없습니다. 프로젝트 루트의 .env 파일을 확인하세요."
    )

print("=== 삼행시 생성기 ===")
print("원하는 세 글자 단어나 이름을 입력하면 삼행시를 지어드립니다.\n")

# 3. 세 글자 단어 입력받기 (세 글자가 아닐 경우 다시 입력 안내)
while True:
    word = input("세 글자 단어 또는 이름을 입력하세요: ").strip()
    if len(word) == 3:
        break
    print("세 글자의 단어를 입력해 주세요.\n")

# 4. 삼행시 생성을 위한 프롬프트 작성
c1, c2, c3 = word[0], word[1], word[2]
prompt = f"""다음 세 글자로 재미있고 자연스러운 삼행시를 지어주세요.
단어: {word}

형식:
{c1}: [첫 번째 문장]
{c2}: [두 번째 문장]
{c3}: [세 번째 문장]

반드시 위 형식에 맞춰 각 행을 해당 글자로 시작해서 출력해줘."""

# 5. OpenAI API 호출
client = OpenAI(api_key=api_key)
response = client.responses.create(
    model=model,
    input=prompt,
    max_output_tokens=150,
)

# 6. 결과 출력
print("\n=== 완성된 삼행시 ===")
print(response.output_text)
