# PUBG 이스포츠 안내 AI 프로토타입

국내(PWS) 및 국제(PGS, PNC, PGC) 배틀그라운드 이스포츠 대회의 일정과 결과, 대회 정보를 조회할 수 있는 대화형 콘솔 AI 서비스입니다.

## 실행 방법

1. Conda 가상환경 활성화:
   ```bash
   conda activate hateslop-week2
   ```

2. 루트 디렉터리의 `.env` 파일에 API 키가 설정되어 있는지 확인합니다:
   ```env
   OPENAI_API_KEY=your_api_key_here
   OPENAI_MODEL=gpt-4o-mini
   ```

3. 프로그램 실행:
   ```bash
   python projects/sohnmj/app.py
   ```

## 주요 기능 및 예시 질문

- **대회 일정 안내**: "올해 PWS 일정과 경기 진행 방식 알려줘"
- **국제 대회 규정 및 선발**: "PGS와 PGC 진출 자격이 어떻게 돼?"
- **대회 결과 및 브리핑**: "배틀그라운드 글로벌 챔피언십(PGC) 역대 한국팀 성적 브리핑해줘"
- **종료**: `q` 또는 `종료` 입력 시 대화가 종료됩니다.
