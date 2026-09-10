# HATESLOP 5기 2회차 실습

Git과 GitHub, Python 가상환경, 환경변수, Markdown 문서를 한 저장소에서 차례로 연습합니다. 마지막에는 OpenAI API를 한 번 호출하고, Antigravity 같은 에이전트와 함께 작은 AI 프로토타입을 만듭니다.

## 저장소 사용 순서

1. 이 저장소를 본인 GitHub 계정으로 Fork합니다.
2. VS Code의 `Clone Git Repository...`로 본인 Fork를 Clone합니다.
3. `week2-{GITHUB_ID}` 형식의 branch를 만듭니다.
4. `projects/{GITHUB_ID}/IDEA.md`에 만들고 싶은 AI 프로토타입을 한두 문장으로 적습니다.
5. `IDEA.md`만 Commit·Push하고, GitHub 연결을 확인하는 첫 Pull Request를 만듭니다.
6. 운영진이 첫 Pull Request를 Merge하거나 Close하면, 새 `assignment-{GITHUB_ID}` branch를 만듭니다.
7. 새 branch에서 AI 프로토타입을 만들고, 두 번째 Pull Request로 제출합니다.

`{GITHUB_ID}`는 중괄호까지 포함해 입력하는 문자가 아니라 본인의 실제 GitHub 아이디로 바꿉니다.

첫 Pull Request는 Git과 GitHub 연결을 확인하는 연습이고, 두 번째 Pull Request는 과제 제출입니다. 폴더는 결과물을 구분하기 위한 것이고, branch는 서로 다른 Pull Request를 분리하는 작업선입니다.

첫 Pull Request가 정리된 뒤에는 아래 명령으로 과제 branch를 만듭니다.

```bash
git switch week2-{GITHUB_ID}
git switch -c assignment-{GITHUB_ID}
```

## 프로젝트 구조

```text
.
├── projects/
│   ├── README.md
│   └── {GITHUB_ID}/           # 과제에서 새로 만듦
│       ├── IDEA.md
│       └── app.py
├── .env.example
├── .gitignore
├── main.py
├── PROJECT_HARNESS.md
├── requirements.txt
├── tools/
│   └── check_submission.py
└── README.md
```

## Python 환경 준비

수업에서는 Conda의 `hateslop-week2` 환경을 사용합니다.

```bash
conda create -n hateslop-week2 python=3.12
conda activate hateslop-week2
pip install -r requirements.txt
```

Windows에서는 아래 명령으로 `.env`를 만들고, macOS에서는 `cp .env.example .env`를 사용합니다.

```powershell
Copy-Item .env.example .env
```

`.env`의 `OPENAI_API_KEY`에는 발급받은 Key를 입력합니다. 실제 Key를 코드, Pull Request, 캡처 화면에 넣지 않습니다.

## 실행

```bash
python main.py
```

질문을 한 번 입력해 짧은 응답이 출력되면 기본 실습은 완료입니다.

## Git에서 제외되었는지 확인

```bash
git check-ignore -v .env
git status --short
```

`.env`는 첫 번째 명령의 결과에 나타나고, 두 번째 명령의 변경 목록에는 나타나지 않아야 합니다.

## AI 프로토타입 과제

첫 Pull Request가 정리된 뒤 과제 branch로 이동합니다. 기본 API 호출이 확인되면 `projects/{GITHUB_ID}/` 폴더 안에서 `IDEA.md`와 `app.py`를 완성합니다.

`IDEA.md`에는 만들고 싶은 것을 한두 문장으로 적습니다. 예를 들어 “사용자가 적은 여행 취향을 받아 1일 여행 코스를 추천해 주는 서비스”처럼 시작하면 됩니다.

Antigravity에서 저장소 폴더를 열고 아래처럼 요청합니다.

```text
먼저 저장소 최상위의 PROJECT_HARNESS.md를 읽고 지켜 주세요.
projects/{GITHUB_ID}/IDEA.md를 읽고,
이 폴더 안에 간단한 대화형 AI 프로토타입을 만들어 주세요.
`python projects/{GITHUB_ID}/app.py`로 실행할 수 있어야 합니다.
API Key는 프로젝트 최상위의 .env에서만 읽고 코드에 넣지 마세요.
```

완성 뒤에는 직접 실행합니다.

```bash
python projects/{GITHUB_ID}/app.py
```

변경 내용을 확인한 뒤 `projects/{GITHUB_ID}`를 Commit하고 아래처럼 과제 branch를 Push합니다.

```bash
git push -u origin assignment-{GITHUB_ID}
```

GitHub에서 `assignment-{GITHUB_ID}` branch로 두 번째 Pull Request를 만듭니다. API Key와 `.env` 내용은 Pull Request나 화면 캡처에 포함하지 않습니다.
