from __future__ import annotations

import sys
import re
from pathlib import Path


ALLOWED_FILES = {"IDEA.md", "app.py", "README.md"}
FORBIDDEN_MARKERS = (
    "streamlit",
    "flask",
    "fastapi",
    "django",
    "react",
    "next.js",
    "vite",
)


def main() -> int:
    if len(sys.argv) != 2:
        print("사용법: python tools/check_submission.py {GITHUB_ID}")
        return 2

    github_id = sys.argv[1]
    root = Path(__file__).resolve().parents[1]
    project_dir = root / "projects" / github_id

    errors: list[str] = []

    if not project_dir.is_dir():
        errors.append(f"제출 폴더가 없습니다: projects/{github_id}/")
    else:
        files = [path for path in project_dir.rglob("*") if path.is_file()]
        for path in files:
            if path.relative_to(project_dir).as_posix() not in ALLOWED_FILES:
                errors.append(f"허용하지 않는 파일입니다: {path.relative_to(root)}")

        idea_path = project_dir / "IDEA.md"
        app_path = project_dir / "app.py"

        if not idea_path.is_file():
            errors.append("IDEA.md가 없습니다.")
        if not app_path.is_file():
            errors.append("app.py가 없습니다.")

        if app_path.is_file():
            app_text = app_path.read_text(encoding="utf-8")
            line_count = len(app_text.splitlines())

            if line_count > 250:
                errors.append(f"app.py가 {line_count}줄입니다. 250줄 이하로 줄여 주세요.")
            if "client.responses.create" not in app_text:
                errors.append("Responses API 호출이 없습니다.")
            output_limit = re.search(r"max_output_tokens\s*=\s*(\d+)", app_text)
            if output_limit is None:
                errors.append("max_output_tokens 제한이 없습니다.")
            elif int(output_limit.group(1)) > 200:
                errors.append("max_output_tokens는 200 이하여야 합니다.")

            model_names = set(re.findall(r"gpt-[A-Za-z0-9.-]+", app_text))
            if "OPENAI_MODEL" not in app_text:
                errors.append("OPENAI_MODEL 환경변수를 읽지 않습니다.")
            if "gpt-4o-mini" not in model_names:
                errors.append("gpt-4o-mini 기본값이 없습니다.")
            elif model_names != {"gpt-4o-mini"}:
                errors.append("gpt-4o-mini 이외의 모델명이 코드에 있습니다.")

            lower_text = app_text.lower()
            for marker in FORBIDDEN_MARKERS:
                if marker in lower_text:
                    errors.append(f"허용하지 않는 프레임워크 또는 도구가 감지되었습니다: {marker}")

    if errors:
        print("제출 전 확인 실패:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("제출 전 확인 통과")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
