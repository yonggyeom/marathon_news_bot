# GitHub Actions 설정 가이드

컴퓨터가 꺼져있어도 스마트폰으로 실행 가능한 자동화 시스템입니다.

## 📋 준비사항

- GitHub 계정
- GitHub 모바일 앱 (스마트폰 수동 실행용)

## 🚀 설정 단계

### 1. GitHub 저장소 생성

1. GitHub 웹사이트 접속 (https://github.com)
2. 우측 상단 "+" → "New repository" 클릭
3. 저장소 설정:
   - **Repository name**: `marathon_news_bot`
   - **Privacy**: Private (추천) 또는 Public
   - **README 추가 체크 해제** (이미 있음)
4. "Create repository" 클릭

### 2. 환경 변수 설정 (GitHub Secrets)

> ⚠️ **중요**: API 키를 코드에 직접 넣지 마세요!

1. 생성한 저장소 페이지에서 **Settings** 탭 클릭
2. 왼쪽 메뉴: **Secrets and variables** → **Actions** 클릭
3. **New repository secret** 버튼 클릭
4. 다음 3개의 Secret 추가:

   **Secret 1:**
   - Name: `NOTION_API_KEY`
   - Secret: (`.env` 파일의 NOTION_API_KEY 값 복사)

   **Secret 2:**
   - Name: `NOTION_DATABASE_ID`
   - Secret: (`.env` 파일의 NOTION_DATABASE_ID 값 복사)

   **Secret 3:**
   - Name: `OPENAI_API_KEY`
   - Secret: (`.env` 파일의 OPENAI_API_KEY 값 복사)

### 3. 코드 푸시

PowerShell 또는 Git Bash에서 실행:

```bash
cd "C:\Users\winde\Documents\Antigravity\marathon_news_bot"

# Git 초기화 (처음만)
git init

# 모든 파일 추가 (.gitignore가 자동으로 .env 제외)
git add .

# 첫 커밋
git commit -m "Initial commit: Marathon News Bot with GitHub Actions"

# GitHub 저장소 연결 (YOUR_USERNAME을 본인 계정으로 변경)
git remote add origin https://github.com/YOUR_USERNAME/marathon_news_bot.git

# 푸시
git branch -M main
git push -u origin main
```

### 4. Actions 활성화 확인

1. GitHub 저장소 페이지에서 **Actions** 탭 클릭
2. "Marathon News Bot" workflow가 보이면 성공!

## 📱 스마트폰에서 수동 실행

### GitHub 모바일 앱 사용 (추천)

1. **GitHub 모바일 앱** 설치 (iOS/Android)
2. 앱 실행 후 로그인
3. `marathon_news_bot` 저장소 선택
4. 하단 메뉴: **Actions** 탭
5. "Marathon News Bot" 선택
6. 우측 상단 **Run workflow** 버튼
7. Branch: `main` 선택
8. **Run workflow** 클릭

### 웹 브라우저 사용

1. 스마트폰 브라우저에서 GitHub 접속
2. 저장소 → Actions 탭
3. "Marathon News Bot" → "Run workflow"
4. "Run workflow" 확인

## ⏰ 자동 실행 스케줄

- **오전 8시** (KST): 매일 자동 실행
- **오후 6시** (KST): 매일 자동 실행

## 📊 실행 로그 확인

1. GitHub 저장소 → **Actions** 탭
2. 최근 실행 목록에서 원하는 실행 클릭
3. "run-bot" 클릭하여 상세 로그 확인
4. 생성된 스크립트는 **Artifacts**에서 다운로드 가능

## 🔧 문제 해결

### Workflow가 보이지 않는 경우
- `.github/workflows/marathon_bot.yml` 파일이 정확히 푸시되었는지 확인
- Actions 탭에서 "I understand my workflows, go ahead and enable them" 클릭

### Secret 오류
- Settings → Secrets and variables → Actions에서 3개 Secret 모두 추가되었는지 확인
- Secret 값에 따옴표나 공백이 추가로 들어가지 않았는지 확인

### ChromeDriver 오류
- Workflow 파일이 최신 버전인지 확인
- 대부분 자동으로 해결됨 (workflow에서 자동 설치)

### 실행은 되는데 결과가 없는 경우
- Actions → 실행 로그에서 에러 메시지 확인
- Notion API 키가 유효한지 확인
- 데이터베이스 ID가 정확한지 확인

## 💰 비용

**완전 무료!**
- GitHub Actions: 월 2,000분 무료 (Public repo는 무제한)
- 이 봇은 실행당 약 3~5분 소요
- 하루 2회 × 30일 = 60회 × 5분 = 300분/월
- 월 무료 한도 내에서 충분히 사용 가능

## 🔄 코드 업데이트 방법

코드 수정 후:

```bash
cd "C:\Users\winde\Documents\Antigravity\marathon_news_bot"
git add .
git commit -m "업데이트 내용 설명"
git push
```

푸시하면 자동으로 GitHub에 반영됩니다.

## ⭐ 추가 팁

### 실행 시간 변경
`.github/workflows/marathon_bot.yml` 파일의 cron 값 수정:
```yaml
schedule:
  - cron: '0 23 * * *'  # 8시 KST
  - cron: '0 9 * * *'   # 18시 KST
```

### 알림 설정
GitHub 모바일 앱 → Settings → Notifications에서 Actions 알림 활성화

### 저장소를 Private로 설정
Settings → Danger Zone → Change repository visibility
