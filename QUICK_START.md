# Marathon News Bot - 빠른 시작 가이드

## ✅ 설정 완료 확인

### 1. GitHub 저장소 확인
https://github.com/yonggyonkim/marathon_news_bot 접속
- 코드 파일들이 보이면 성공!
- `.github/workflows/marathon_bot.yml` 파일이 있는지 확인

### 2. GitHub Actions 확인
- 저장소 → **Actions** 탭 클릭
- "Marathon News Bot" workflow가 보이면 성공!

## 📱 스마트폰으로 수동 실행하기

### GitHub 모바일 앱 (추천)
1. **App Store/Play Store**에서 "GitHub" 앱 다운로드
2. 앱 실행 후 로그인
3. **Repositories** → `marathon_news_bot` 선택
4. 하단 **Actions** 탭
5. "Marathon News Bot" 선택
6. 우측 상단 **"..."** → **"Run workflow"**
7. Branch: `main` 선택
8. **"Run workflow"** 버튼 클릭

### 모바일 웹 브라우저
1. https://github.com/yonggyonkim/marathon_news_bot/actions
2. "Marathon News Bot" 클릭
3. 우측 "Run workflow" 드롭다운
4. "Run workflow" 버튼 클릭

## ⏰ 자동 실행 스케줄

설정 완료! 다음 시간에 자동 실행됩니다:
- **매일 오전 8시** (KST)
- **매일 오후 6시** (KST)

## 📊 실행 결과 확인

### PC에서
1. https://github.com/yonggyonkim/marathon_news_bot/actions
2. 최근 실행 클릭
3. "run-bot" → 로그 확인
4. "Artifacts" → 생성된 스크립트 다운로드

### 스마트폰에서
1. GitHub 앱 → Actions 탭
2. 실행 항목 클릭
3. 로그 확인

## 🔧 문제 해결

### Actions가 실행되지 않는 경우
1. GitHub 저장소 → **Settings**
2. 왼쪽 **Actions** → **General**
3. "Allow all actions and reusable workflows" 선택
4. **Save**

### Secret 오류가 나는 경우
Settings → Secrets → Actions 에서:
- `NOTION_API_KEY` ✓
- `NOTION_DATABASE_ID` ✓
- `OPENAI_API_KEY` ✓
모두 있는지 확인

### ChromeDriver 오류
- 대부분 자동으로 해결됨
- 실행 로그에서 오류 확인 가능

## 🎯 첫 실행 테스트

**지금 바로 테스트:**
1. GitHub → Actions → "Marathon News Bot"
2. "Run workflow" 클릭
3. 약 5분 후 결과 확인

성공하면:
- Notion에 새 이벤트 추가됨
- 교차검증 완료 (AI 생성 이벤트만)
- `output/` 폴더에 스크립트 생성됨

## 📝 다음 스케줄 실행

**오늘 오후 6시** 또는 **내일 오전 8시**에 자동으로 실행됩니다!

## 💰 비용

**완전 무료!**
- GitHub Actions 월 2,000분 무료
- 이 봇은 약 5분/회 소요
- 하루 2회 × 30일 = 300분/월 (충분함)

## 🆘 도움말

- GitHub Actions 공식 문서: https://docs.github.com/actions
- Notion API 문서: https://developers.notion.com
- 문제 발생 시: GitHub Issues 활용
