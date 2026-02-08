# Marathon News Bot 🏃‍♂️

마라톤 대회 정보를 자동으로 수집하고 Notion에 동기화하는 봇입니다.

## 주요 기능

- 🔍 **다중 소스 크로스검증**: roadrun.co.kr + runninglife.co.kr
- 📅 **Notion 자동 동기화**: 새로운 대회 자동 등록
- ⏰ **스마트 알림**: 접수 시작일 오전 9시 KST
- 🤖 **AI 생성 스크립트**: YouTube용 대회 소개 스크립트 자동 생성
- ☁️ **클라우드 실행**: GitHub Actions로 컴퓨터 없이 실행
- 📱 **스마트폰 제어**: 언제 어디서나 수동 실행 가능

## 빠른 시작

### 로컬 실행

```bash
# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정 (.env 파일 생성)
NOTION_API_KEY=your_api_key
NOTION_DATABASE_ID=your_database_id
OPENAI_API_KEY=your_openai_key

# 실행
python main.py
```

### GitHub Actions 설정 (추천)

컴퓨터가 꺼져있어도 자동 실행하고 스마트폰으로 제어하려면:

📖 **[GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md)** 참조

## 실행 스케줄

- 오전 8시 (KST)
- 오후 6시 (KST)

## 문서

- **설정 가이드**: [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md)
- **전체 기능 소개**: [walkthrough.md](./.gemini/antigravity/brain/426e40a3-8c88-438c-8cfa-2c03d2e4165f/walkthrough.md)
- **로컬 스케줄러**: [SCHEDULER_SETUP.md](SCHEDULER_SETUP.md)

## 기술 스택

- Python 3.11+
- Selenium (웹 스크래핑)
- Notion API
- OpenAI API
- GitHub Actions

## 라이센스

MIT
