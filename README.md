# HATESLOP 5기 2회차 실습

Git과 GitHub, Python 가상환경, 환경변수, Markdown 문서를 한 저장소에서 차례로 연습합니다. 마지막에는 OpenAI API를 한 번 호출하고, Antigravity와 함께 작은 AI 프로토타입을 만듭니다.

## 저장소 사용 순서

1. 이 저장소를 본인 GitHub 계정으로 Fork합니다.
2. VS Code의 `Clone Git Repository...`로 본인 Fork를 Clone합니다.
3. `week2-{GITHUB_ID}` 형식의 branch를 만듭니다.
4. `participants/_template.md`를 복사해 `participants/{GITHUB_ID}.md`를 만듭니다.
5. 복사한 파일에 GitHub ID와 아무 문장이나 한 줄 적습니다.
6. 변경을 Commit하고 본인 Fork에 Push한 뒤 **Git 연습 Pull Request**를 만듭니다.

`{GITHUB_ID}`는 중괄호까지 포함해 입력하는 문자가 아니라 본인의 실제 GitHub 아이디로 바꿉니다.

Git 연습 Pull Request는 Fork·Branch·Commit·Push 흐름을 확인하는 용도입니다. 수업 중 안내에 따라 마무리하며, 실제 과제 제출은 아래의 `assignment-{GITHUB_ID}` branch에서 별도의 Pull Request로 진행합니다.

## 프로젝트 구조

```text
.
├── .github/
│   └── pull_request_template.md
├── participants/
│   └── _template.md
├── .env.example
├── .gitignore
├── main.py
├── app.py                  # 과제에서 새로 만듦
├── requirements.txt
├── TASK.md
└── README.md
```

## Python 환경 준비

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

### macOS zsh

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
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

## Antigravity AI 프로토타입 과제

기본 API 호출이 확인되면 `main`에서 새 과제 branch를 만듭니다.

```bash
git switch main
git pull origin main
git switch -c assignment-{GITHUB_ID}
```

`TASK.md`에는 **AI 아이디어 구체화 도우미**를 만드는 목표·제약·완료 조건이 들어 있습니다. Antigravity에게 먼저 계획만 요청하고, 계획을 확인한 뒤 구현을 승인합니다. `app.py`를 만든 뒤에는 다음 명령으로 직접 실행합니다.

```bash
streamlit run app.py
```

마지막으로 `app.py`, `README.md`, `requirements.txt`의 변경을 검토해 Commit·Push하고, `assignment-{GITHUB_ID}` branch로 **과제 Pull Request**를 만듭니다. API Key와 `.env` 내용은 Pull Request나 화면 캡처에 포함하지 않습니다.
