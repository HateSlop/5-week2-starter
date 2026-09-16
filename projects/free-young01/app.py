"""입력한 단어로 N행시를 만들어 주는 간단한 터미널 프로토타입."""

from pathlib import Path

from dotenv import dotenv_values
from openai import OpenAI


ROOT_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = ROOT_DIR / ".env"


def get_client() -> tuple[OpenAI | None, str]:
    """최상위 .env만 읽어 OpenAI 클라이언트를 준비한다."""
    settings = dotenv_values(ENV_PATH)
    api_key = settings.get("OPENAI_API_KEY")
    model = settings.get("OPENAI_MODEL") or "gpt-4o-mini"

    if not api_key:
        print("API 키를 찾을 수 없습니다. 프로젝트 최상위 .env를 확인해 주세요.")
        return None, model
    return OpenAI(api_key=api_key), model


def create_poem(client: OpenAI, model: str, word: str) -> str:
    """사용자 입력당 단 한 번의 API 요청으로 N행시를 만든다."""
    prompt = f"""당신은 재치 있는 한국어 N행시 작가입니다.
사용자가 준 단어는 '{word}'입니다.
단어의 글자 수는 {len(word)}자입니다. 각 글자로 시작하는 N행시를 정확히 {len(word)}줄로 지어 주세요.
각 줄은 해당 순서의 글자로 반드시 시작해야 합니다.
반드시 사용자가 웃을 수 있게 유머러스하게 작성해 주세요.
설명, 제목, 이모지, 따옴표는 빼고 시만 출력하세요."""
    response = client.responses.create(
        model=model,
        input=prompt,
        max_output_tokens=200,
    )
    return response.output_text.strip()


def main() -> None:
    print("=" * 42)
    print("        개꿀잼 N행시 생성기")
    print("단어를 입력해 보세요. 공백은 빼고 N행시를 지어요. (종료: q)")
    print("=" * 42)

    client, model = get_client()
    if client is None:
        return

    while True:
        try:
            word = "".join(input("\n단어 > ").split())
        except (EOFError, KeyboardInterrupt):
            print("\n다음에 또 놀러 오세요!")
            break

        if word.lower() in {"q", "quit", "exit", "종료"}:
            print("다음에 또 놀러 오세요!")
            break
        if not word:
            print("단어를 입력해 주세요.")
            continue

        try:
            poem = create_poem(client, model, word)
            print("\n" + (poem or "N행시를 만들지 못했어요. 다시 시도해 주세요."))
        except Exception:
            print("요청을 처리하지 못했어요. 인터넷 연결과 API 설정을 확인해 주세요.")


if __name__ == "__main__":
    main()
