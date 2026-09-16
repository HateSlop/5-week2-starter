# HSK 맞춤형 학습 플래너 (AI 프로토타입)

사용자가 목표로 하는 HSK 급수와 취득 시기(준비 기간)를 입력하면 OpenAI API를 활용하여 맞춤형 핵심 학습 플랜을 간결하게 제시해 주는 콘솔형 AI 프로토타입입니다.

## 실행 방법

1. 프로젝트 루트 디렉터리에 `.env` 파일을 생성하고 OpenAI API 키를 설정합니다.
   ```env
   OPENAI_API_KEY=your_api_key_here
   OPENAI_MODEL=gpt-4o-mini
   ```

2. 터미널에서 다음 명령어를 실행합니다.
   ```bash
   python projects/jeongin82/app.py
   ```

3. 안내에 따라 목표 HSK 급수, 취득 시기, 현재 실력을 입력하면 AI 학습 플랜이 출력됩니다.
