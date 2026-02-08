# 스케줄 설정 가이드

## 자동 설정 (권장)

PowerShell 스크립트를 사용하여 자동으로 스케줄 작업을 생성합니다:

1. **PowerShell을 관리자 권한으로 실행**
   - 시작 메뉴에서 "PowerShell" 검색
   - 우클릭 → "관리자 권한으로 실행"

2. **스크립트 디렉토리로 이동**
   ```powershell
   cd "C:\Users\winde\Documents\Antigravity\marathon_news_bot"
   ```

3. **실행 정책 임시 변경 (필요시)**
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
   ```

4. **스케줄 설정 스크립트 실행**
   ```powershell
   .\setup_scheduler.ps1
   ```

## 수동 설정

PowerShell 스크립트 실행이 어려운 경우 Task Scheduler GUI를 사용:

1. **작업 스케줄러 열기**
   - `Win + R` → `taskschd.msc` 입력

2. **기본 작업 만들기**
   - 오른쪽 패널: "작업 만들기" 클릭

3. **일반 탭**
   - 이름: `MarathonNewsBot`
   - 설명: `Marathon News Bot - 8시와 18시에 실행`
   - "사용자의 로그온 여부에 관계없이 실행" 선택
   - "가장 높은 수준의 권한으로 실행" 체크

4. **트리거 탭**
   - "새로 만들기" 클릭
   - 작업 시작: "일정에 따라"
   - 설정: "매일"
   - 시작 시간: `오전 8:00`
   - 확인

   - 다시 "새로 만들기" 클릭
   - 작업 시작: "일정에 따라"
   - 설정: "매일"
   - 시작 시간: `오후 6:00`
   - 확인

5. **동작 탭**
   - "새로 만들기" 클릭
   - 동작: "프로그램 시작"
   - 프로그램/스크립트: `C:\Users\winde\Documents\Antigravity\marathon_news_bot\run.bat`
   - 시작 위치: `C:\Users\winde\Documents\Antigravity\marathon_news_bot`
   - 확인

6. **조건 탭**
   - "다음 네트워크 연결을 사용할 수 있는 경우에만 시작" 체크
   - "컴퓨터의 전원을 AC 전원으로 사용할 때만 작업 시작" 해제
   - "작업을 실행하기 위해 절전 모드 종료" 체크

7. **설정 탭**
   - "요청 시 작업 실행 허용" 체크
   - "작업 실행 실패 시 다시 시작 간격": `1분`, 최대 `3회`

8. **확인** 클릭

## 확인 및 테스트

### 스케줄 작업 확인
```powershell
Get-ScheduledTask -TaskName "MarathonNewsBot"
```

### 수동 실행 테스트
```powershell
Start-ScheduledTask -TaskName "MarathonNewsBot"
```

### 작업 기록 확인
```powershell
Get-ScheduledTaskInfo -TaskName "MarathonNewsBot"
```

### 작업 삭제
```powershell
Unregister-ScheduledTask -TaskName "MarathonNewsBot" -Confirm:$false
```

## 로그 확인

실행 로그는 다음 위치에서 확인:
- 작업 스케줄러 → MarathonNewsBot → 기록 탭
- 또는 이벤트 뷰어 → Windows 로그 → 응용 프로그램

## 문제 해결

### 작업이 실행되지 않는 경우
1. 작업 스케줄러에서 "MarathonNewsBot" 우클릭 → "실행"으로 수동 테스트
2. 기록 탭에서 오류 메시지 확인
3. `run.bat` 파일 경로가 정확한지 확인
4. Python 및 환경 변수(.env) 설정 확인

### 권한 문제
- PowerShell을 관리자 권한으로 실행했는지 확인
- 작업 스케줄러에서 "가장 높은 수준의 권한으로 실행" 설정 확인
