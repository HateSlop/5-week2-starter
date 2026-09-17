"""터미널에서 듣고 맞히는 음감 퀴즈. 외부 패키지: openai, python-dotenv."""

import json
import math
from pathlib import Path
import random
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import time
import wave

from dotenv import dotenv_values
from openai import APIConnectionError, APIError, AuthenticationError, OpenAI, RateLimitError


ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
NAMES = ("도", "도#", "레", "레#", "미", "파", "파#", "솔", "솔#", "라", "라#", "시")
FLATS = {1: "레b", 3: "미b", 6: "솔b", 8: "라b", 10: "시b"}
BASE_NOTES = dict(zip(("도", "레", "미", "파", "솔", "라", "시"), (0, 2, 4, 5, 7, 9, 11)))
BASE_NOTES.update(dict(zip("cdefgab", (0, 2, 4, 5, 7, 9, 11))))
LEVELS = {"하": 1, "중": 2, "상": 3}
SCALE = (0, 2, 4, 5, 7, 9, 11, 12)

def section(title):
    print(f"\n{'─' * 44}\n  {title}\n{'─' * 44}")

def read_input(prompt):
    answer = input(prompt).strip()
    if answer.lower() in {"종료", "q", "quit", "exit"}:
        raise EOFError
    return answer

def choose_level():
    section("난이도 선택")
    print("  하 : 한 음     중 : 두 음     상 : 세 음\n")
    while True:
        level = read_input("  난이도 입력 (하 / 중 / 상, 종료: q) › ")
        if level in LEVELS:
            play_scale()
            return level
        print("  하, 중, 상 중 하나를 입력해 주세요.")

def parse_notes(answer, count):
    answer = answer.replace("♯", "#").replace("♭", "b").replace("샵", "#").replace("플랫", "b")
    tokens = re.split(r"[\s,]+", answer.strip().lower())
    if len(tokens) != count:
        example = " ".join(("도", "미", "솔")[:count])
        raise ValueError(f"음 {count}개를 입력해 주세요. 입력 예: {example}")
    notes = []
    for token in tokens:
        match = re.fullmatch(r"(도|레|미|파|솔|라|시|[a-g])([#b]?)", token)
        if not match:
            raise ValueError("계이름 또는 영문 음이름을 입력해 주세요. 예: 도#, 레b, C#, Db")
        base, accidental = match.groups()
        notes.append((BASE_NOTES[base] + {"": 0, "#": 1, "b": -1}[accidental]) % 12)
    if len(set(notes)) != count:
        raise ValueError("서로 다른 음을 입력해 주세요. 도#과 레b는 같은 음입니다.")
    return sorted(notes)

def write_tone(path, notes, duration=1.5, scale=False):
    """음계를 한 파일에 합성해 재생기 재실행 없이 잇고 표시 시점을 반환한다."""
    rate = 44100
    sequence = [(notes, duration, 0, "")]
    if scale:
        sequence = [([note], 0.55, 0.04, NAMES[note % 12]) for note in SCALE]
        sequence.append(([SCALE[0]], 2.0, 0, '\n\n  이 소리가 "도"입니다. 처음의 도를 다시 들어 보세요.'))
    data, cues = bytearray(), []
    for chord, length, gap, label in sequence:
        if label:
            cues.append((len(data) / (2 * rate), label))
        frames = int(rate * length)
        frequencies = [440.0 * 2 ** ((note - 9) / 12) for note in chord]
        for i in range(frames):
            fade = min(1.0, i / (rate * 0.03), (frames - 1 - i) / (rate * 0.05))
            value = sum(math.sin(2 * math.pi * freq * i / rate) for freq in frequencies)
            data.extend(struct.pack("<h", int(10000 * fade * value / len(chord))))
        data.extend(b"\0\0" * int(rate * gap))
    with wave.open(str(path), "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(rate)
        audio.writeframes(data)
    return cues

def play_notes(notes, duration=1.5, scale=False):
    # 정답이 파일명에 드러나지 않도록 임시 파일을 쓰고 재생 후 삭제한다.
    try:
        with tempfile.TemporaryDirectory(prefix="pitch-quiz-") as directory:
            path = Path(directory) / "quiz.wav"
            cues = write_tone(path, notes, duration, scale)
            if sys.platform == "win32":
                code = "import sys,winsound; winsound.PlaySound(sys.argv[1], winsound.SND_FILENAME | winsound.SND_NODEFAULT)"
                command = [sys.executable, "-c", code, str(path)]
            else:
                commands = ("afplay",) if sys.platform == "darwin" else ("aplay", "paplay")
                player = next((shutil.which(cmd) for cmd in commands if shutil.which(cmd)), None)
                if not player:
                    raise RuntimeError("재생 도구가 없습니다. macOS/Windows 또는 aplay·paplay가 있는 Linux에서 실행하세요.")
                command = [player, str(path)]
            with subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) as process:
                try:
                    start = time.monotonic()
                    for offset, label in cues:
                        try:
                            process.wait(timeout=max(0, start + offset - time.monotonic()))
                        except subprocess.TimeoutExpired:
                            print(label, end="  ", flush=True)
                        else:
                            raise OSError("Audio stopped early")
                    if process.wait(timeout=10) != 0:
                        raise OSError("Audio playback failed")
                finally:
                    if process.poll() is None:
                        process.kill()
                    process.wait()
    except (OSError, subprocess.SubprocessError):
        raise RuntimeError("소리를 재생하지 못했습니다. 오디오 출력 장치를 확인한 뒤 다시 실행해 주세요.") from None

def labels(notes):
    return " · ".join(f"{NAMES[n]}({FLATS[n]})" if n in FLATS else NAMES[n] for n in notes)

def play_scale():
    section("음계 듣기 · 소리를 기억해 보세요")
    print("  ", end="", flush=True)
    try:
        play_notes([], scale=True)
    finally:
        print("\n")

def make_question(client, model, level):
    count = LEVELS[level]
    candidates = [random.sample(range(12), count) for _ in range(3)]
    try:
        response = client.responses.create(
            model=model,
            instructions=(
                '음감 퀴즈를 출제하라. 후보 중 한 조합을 골라 {"notes": [정수 목록]} JSON만 반환하라. '
                "각 정수는 도부터 시까지 반음 단위의 음 번호 0~11이다. 설명이나 코칭을 붙이지 마라."
            ),
            input=f"난이도: {level}, 서로 다른 {count}음. 후보: {json.dumps(candidates)}. JSON으로 답하라.",
            text={"format": {"type": "json_object"}},
            max_output_tokens=200,
            store=False,
        )
        notes = json.loads(response.output_text)["notes"]
        if (response.status != "completed" or not isinstance(notes, list) or len(notes) != count
                or any(type(note) is not int or not 0 <= note <= 11 for note in notes)
                or len(set(notes)) != count):
            raise ValueError
        return sorted(notes)
    except AuthenticationError:
        print("  연결 실패: 최상위 .env의 OPENAI_API_KEY 설정을 확인해 주세요.")
    except RateLimitError:
        print("  출제를 잠시 이용할 수 없습니다. API 사용량 또는 요청 한도를 확인해 주세요.")
    except APIConnectionError:
        print("  출제 연결이 끊겼거나 시간이 초과되었습니다. 네트워크를 확인해 주세요.")
    except APIError:
        print("  출제에 실패했습니다. API 상태와 .env의 OPENAI_MODEL 설정을 확인해 주세요.")
    except (ValueError, KeyError, TypeError):
        print("  출제된 음을 확인할 수 없습니다. 다음 문제를 선택해 주세요.")
    return None

def next_action(level):
    while True:
        print("\n  [Enter] 다음 문제    [음계] 도레미파솔라시도\n  [난이도] 변경        [q] 종료")
        action = read_input("\n  선택 › ").lower()
        if action == "":
            return level
        if action in {"음계", "s"}:
            play_scale()
        elif action == "난이도":
            return choose_level()
        else:
            print("  Enter를 누르거나 음계, 난이도, q를 입력해 주세요.")

def quiz(client, model):
    section("듣고 맞히는 음감 퀴즈")
    print("  도 · 레 · 미 · 파 · 솔 · 라 · 시  (#/b 포함)\n  먼저 음계를 듣고, 문제의 음을 맞혀 보세요.\n  컴퓨터 볼륨을 켜 주세요.")
    total = score = 0
    try:
        level = choose_level()
        while True:
            count = LEVELS[level]
            section(f"문제 {total + 1:02d}  |  난이도 {level}  |  {count}음")
            print("  문제를 준비하고 있어요...", flush=True)
            expected = make_question(client, model, level)
            if expected is None:
                level = next_action(level)
                continue
            print("  소리를 들어 주세요.\n", flush=True)
            play_notes(expected)
            example = " / ".join(("도", "도#", "C")) if count == 1 else " ".join(("도", "미", "솔")[:count])
            print(f"  입력 예: {example}  ·  #/b 사용 가능")
            print("  [다시] 재생   [난이도] 변경   [q] 종료\n")
            while True:
                raw = read_input("  들린 음 › ")
                if raw.lower() in {"다시", "r"}:
                    play_notes(expected)
                    continue
                if raw == "난이도":
                    level = choose_level()
                    break
                try:
                    answer = parse_notes(raw, count)
                except ValueError as error:
                    print(f"  {error}")
                    continue
                total += 1
                score += answer == expected
                matched = len(set(answer) & set(expected))
                section("정답!" if answer == expected else "오답")
                print(f"  내 답     {raw}\n  정답      {labels(expected)}")
                print(f"\n  맞힌 음   {matched}/{count}     누적 정답   {score}/{total}")
                level = next_action(level)
                break
    except (EOFError, KeyboardInterrupt):
        print("\n  퀴즈를 종료합니다.")
    finally:
        section(f"최종 기록  |  {total}문제 중 {score}문제 정답")

def main():
    try:
        # 환경변수나 다른 .env 파일에서 키를 가져오거나 보간하지 않는다.
        config = dotenv_values(ENV_PATH, interpolate=False)
        api_key = (config.get("OPENAI_API_KEY") or "").strip()
        if not api_key:
            print("저장소 최상위 .env에 OPENAI_API_KEY를 설정한 뒤 실행해 주세요.")
            return 1
        model = (config.get("OPENAI_MODEL") or "").strip() or "gpt-4o-mini"
        with OpenAI(api_key=api_key, base_url="https://api.openai.com/v1",
                    max_retries=0, timeout=20.0) as client:
            quiz(client, model)
        return 0
    except RuntimeError as error:
        print(error)
        return 1
    except (OSError, UnicodeError, ValueError, APIError):
        # 원본 예외에는 인증 정보가 포함될 수 있으므로 출력하지 않는다.
        print("실행하지 못했습니다. 최상위 .env 설정과 오디오 장치를 확인해 주세요.")
        return 1
    except (EOFError, KeyboardInterrupt):
        print("\n종료합니다.")
        return 0

if __name__ == "__main__":
    raise SystemExit(main())
