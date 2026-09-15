"""Correct a batch of bibliography entries to APA 7th edition.

The model returns a structured array rather than free-form prose.  That keeps
the original order and makes an uncertain/missing field visible to the user.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI


MAX_CHARACTERS_PER_REQUEST = 24_000

SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "references": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "input_index": {"type": "integer"},
                    "source_type": {
                        "type": "string",
                        "enum": ["book", "journal_article", "webpage", "report", "chapter", "thesis", "other", "uncertain"],
                    },
                    "apa_markdown": {"type": "string"},
                    "needs_review": {"type": "boolean"},
                    "review_reasons": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["input_index", "source_type", "apa_markdown", "needs_review", "review_reasons"],
            },
        }
    },
    "required": ["references"],
}

INSTRUCTIONS = """You are an exacting APA Style 7th edition bibliography editor.
The input is a numbered list of one or more raw bibliography entries. Return one
object for every input index, in exactly the same order. Do not merge entries,
drop entries, or create extra entries.

Classify each entry, then correct only its presentation into APA 7 reference-list
format. Use Markdown asterisks only around text that must be italicized. Preserve
the source language. Keep a DOI as https://doi.org/... and use a URL only when it
is supplied or clearly part of the source. Do not invent authors, dates, titles,
publishers, page ranges, volume/issue, DOI, or URL. If a required detail is absent
or the source type cannot be determined reliably, produce the best defensible APA
reference and set needs_review to true with concise Korean review reasons.

Do not add a leading number, bullet, heading, explanation, or citation in
apa_markdown. Correct punctuation, capitalization, ordering, and italics.
"""


def split_entries(raw_text: str) -> list[str]:
    """Split obvious pasted entries while preserving wrapped lines.

    Blank lines, list markers, and numbered list markers are definitive separators.
    A run of plain one-line references is also treated as multiple entries.  For an
    ambiguous wrapped paragraph, keep it together; the model is then told it is one
    entry instead of silently corrupting it.
    """
    text = raw_text.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not text:
        return []

    blocks = [block.strip() for block in re.split(r"\n\s*\n+", text) if block.strip()]
    entries: list[str] = []
    marker = re.compile(r"^\s*(?:\[?\d{1,3}[.)\]]|[-*•])\s+")

    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        marked = [marker.sub("", line) for line in lines if marker.match(line)]
        if marked and len(marked) == len(lines):
            entries.extend(marked)
        elif len(lines) > 1 and all(len(line) >= 35 for line in lines):
            # A common copy/paste format is exactly one complete entry per line.
            entries.extend(lines)
        else:
            entries.append(" ".join(lines))
    return entries


def chunks(entries: list[str]) -> list[list[tuple[int, str]]]:
    result: list[list[tuple[int, str]]] = []
    current: list[tuple[int, str]] = []
    size = 0
    for index, entry in enumerate(entries, start=1):
        item_size = len(entry) + 32
        if item_size > MAX_CHARACTERS_PER_REQUEST:
            raise ValueError(f"{index}번 항목이 너무 깁니다 ({len(entry):,}자). 항목을 나누어 다시 입력하세요.")
        if current and size + item_size > MAX_CHARACTERS_PER_REQUEST:
            result.append(current)
            current, size = [], 0
        current.append((index, entry))
        size += item_size
    if current:
        result.append(current)
    return result


def correct_batch(client: OpenAI, model: str, batch: list[tuple[int, str]]) -> list[dict[str, Any]]:
    numbered_entries = "\n\n".join(f"[{index}] {entry}" for index, entry in batch)
    response = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {"role": "system", "content": INSTRUCTIONS},
            {"role": "user", "content": f"Raw bibliography entries:\n\n{numbered_entries}"},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {"name": "apa_reference_batch", "strict": True, "schema": SCHEMA},
        },
    )
    content = response.choices[0].message.content
    if not content:
        raise RuntimeError("모델이 빈 응답을 반환했습니다.")
    data = json.loads(content)
    expected = [index for index, _ in batch]
    received = [item["input_index"] for item in data["references"]]
    if received != expected:
        raise RuntimeError(f"항목 번호가 일치하지 않습니다. 기대값: {expected}, 응답: {received}")
    return data["references"]


def render(results: list[dict[str, Any]], markdown: bool) -> str:
    lines = ["[APA 7 교정 결과]", ""]
    for item in results:
        reference = item["apa_markdown"]
        if not markdown:
            reference = re.sub(r"\*([^*]+)\*", r"\1", reference)
        lines.append(reference)
        if item["needs_review"]:
            lines.append(f"  ⚠ 검토 필요: {'; '.join(item['review_reasons'])}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="여러 참고문헌을 APA 7판으로 교정합니다.")
    parser.add_argument("file", nargs="?", default="references.txt", help="UTF-8 참고문헌 텍스트 파일 (기본: references.txt)")
    parser.add_argument("--markdown", action="store_true", help="이탤릭체를 Markdown(*)으로 유지합니다.")
    parser.add_argument("--output", type=Path, help="결과를 UTF-8 파일로도 저장합니다.")
    args = parser.parse_args()

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY가 없습니다. .env 파일을 확인하세요.")

    path = Path(args.file)
    try:
        raw_text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise SystemExit(f"{path} 파일을 찾을 수 없습니다.")

    entries = split_entries(raw_text)
    if not entries:
        raise SystemExit("참고문헌 파일 내용이 비어 있습니다.")

    client = OpenAI(api_key=api_key)
    results: list[dict[str, Any]] = []
    for batch in chunks(entries):
        results.extend(correct_batch(client, model, batch))

    output = render(results, markdown=args.markdown or args.output is not None)
    print(output, end="")
    if args.output:
        args.output.write_text(output, encoding="utf-8")
        print(f"저장 완료: {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()