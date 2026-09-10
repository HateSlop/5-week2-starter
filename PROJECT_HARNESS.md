# AI 프로토타입 과제 규칙

이 문서는 Codex, Claude Code, Antigravity 등 어떤 에이전트를 쓰더라도 과제를 시작하기 전에 읽습니다. 먼저 짧은 구현 계획을 보여 주고, 이 규칙 안에서만 수정합니다.

## 작업 범위

- 수정할 수 있는 위치는 `projects/{GITHUB_ID}/`뿐입니다.
- 필수 제출 파일은 `IDEA.md`와 `app.py`입니다.
- 결과를 더 보여 주고 싶다면 같은 폴더에 짧은 `README.md`와 `output/` 폴더를 선택해서 추가할 수 있습니다. `output/`에는 결과 화면 스크린샷만 1~2장(`.png`, `.jpg`, `.jpeg`, `.webp`) 넣습니다.
- `output/`에는 코드·설정 파일·의존성 폴더를 넣지 않습니다. 스크린샷에도 API Key나 `.env` 내용이 보이면 안 됩니다.
- `main.py`, `requirements.txt`, `.env.example`, `.gitignore`, 다른 사람 폴더는 수정하지 않습니다.
- React, Next.js, Vite, Flask, FastAPI, Streamlit, 데이터베이스, 배포 설정을 추가하지 않습니다.

## 프로토타입 기준

- `python projects/{GITHUB_ID}/app.py`로 실행되는 대화형 Python 프로그램을 만듭니다.
- Python 표준 라이브러리, `openai`, `python-dotenv`만 사용합니다. 새 패키지를 설치하거나 추가하지 않습니다.
- `app.py`는 250줄 이하로 유지합니다.
- 사용자 입력 한 번에 OpenAI API 요청은 한 번만 보냅니다. 자동 반복 호출, 병렬 호출, 백그라운드 실행, 무한 재시도는 만들지 않습니다.
- API 응답 길이는 `max_output_tokens=200` 이하로 제한합니다.
- 모델은 `.env`의 `OPENAI_MODEL`을 읽고, 기본값과 안내값은 `gpt-4o-mini`만 사용합니다. 다른 모델명을 코드에 추가하지 않습니다.
- API Key는 프로젝트 최상위 `.env`에서만 읽고, 코드·출력·README·PR 본문에 기록하지 않습니다.

## 더 크게 만들고 싶다면

웹 화면, 새 패키지, 데이터베이스, 배포가 필요한 아이디어는 이 과제 Pull Request에 붙이지 않습니다. 먼저 이 과제의 작은 버전을 제출하고, 확장 버전은 별도 개인 저장소에서 진행합니다. 확장 버전을 소개하고 싶다면 선택 `README.md`에 개인 저장소 링크만 남길 수 있습니다. 이 과제의 코드 리뷰 대상은 계속 `app.py`입니다.

## 완료 전 확인

1. 에이전트가 만든 변경 diff를 읽습니다.
2. Conda `hateslop-week2` 환경에서 직접 실행합니다.
3. 아래 검사기를 실행합니다.

```bash
python tools/check_submission.py {GITHUB_ID}
```

4. `projects/{GITHUB_ID}/`만 Commit하고 Pull Request를 만듭니다.
