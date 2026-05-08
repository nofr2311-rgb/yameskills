# Yame Skills

Claude에서 쓰던 더존 업무 자동화 스킬을 GitHub 웹/모바일에서 실행할 수 있게 옮기는 repo입니다.

가격표 기반 구매신청서/견적 자동화는 별도 repo에서 관리합니다.

- https://github.com/nofr2311-rgb/douzone-quote-bot

이 repo는 그 외 작업, 예를 들면 WEHAGO 신규견적, DM 이메일 추출, 유지보수 보고서 HWPX 생성, PDF 인장 찍기, A10 갑지 생성을 담당합니다.

## 지금 바로 쓸 수 있는 기능

### WEHAGO 신규견적 생성

1. GitHub 모바일 앱이나 웹에서 이 repo의 Issues로 이동합니다.
2. **New issue**를 누릅니다.
3. **WEHAGO 신규견적 생성** 템플릿을 선택합니다.
4. 인바운드/통화 내용을 그대로 붙여넣습니다.
5. Issue를 만들면 Actions가 실행되고, 완료 댓글에 WEHAGO 신규견적 XLSX 링크가 달립니다.

예시:

```text
가상테스트회사에서 WEHAGO 회계 2인, 인사급여 2인, Smart A10 사용료 2인 쓴다고 함. 월납 CLUB.
```

### PDF 인장 찍기

1. GitHub 모바일 앱이나 웹에서 이 repo의 Issues로 이동합니다.
2. **New issue**를 누릅니다.
3. **PDF 인장 찍기** 템플릿을 선택합니다.
4. PDF 파일을 본문에 첨부합니다.
5. 필요하면 page, x, y, size, alpha 값을 입력합니다.
6. Issue를 만들면 Actions가 실행되고, 완료 댓글에 인장 찍힌 PDF 링크가 달립니다.

기본값:

```text
page: 2
x: 493
y: 100
size: 58
alpha: 180
```

### A10 갑지 생성

1. GitHub 모바일 앱이나 웹에서 이 repo의 Issues로 이동합니다.
2. **New issue**를 누릅니다.
3. **A10 갑지 생성** 템플릿을 선택합니다.
4. A10 견적서 xlsx 또는 pdf 파일을 첨부합니다.
5. Issue를 만들면 Actions가 실행되고, 완료 댓글에 갑지 PDF/XLSX 링크가 달립니다.

### DM 이메일 리스트 생성

1. GitHub 모바일 앱이나 웹에서 이 repo의 Issues로 이동합니다.
2. **New issue**를 누릅니다.
3. **DM 이메일 리스트 생성** 템플릿을 선택합니다.
4. 미가공 고객사 Excel 파일을 첨부합니다.
5. Issue를 만들면 Actions가 실행되고, 완료 댓글에 이메일 추출 XLSX 링크가 달립니다.

현재 버전은 엑셀 전체 시트에서 이메일 패턴을 찾고, 중복 제거 후 `이메일(복사용)` 컬럼에 `email@domain.com,` 형식으로 정리합니다.

### 유지보수 보고서 생성

1. GitHub 모바일 앱이나 웹에서 이 repo의 Issues로 이동합니다.
2. **New issue**를 누릅니다.
3. **유지보수 보고서 생성** 템플릿을 선택합니다.
4. 이전 월 HWPX 1개, 온라인상담 PDF 1개, 유선상담 PDF 1개를 첨부합니다.
5. Issue를 만들면 Actions가 실행되고, 완료 댓글에 새 HWPX 링크가 달립니다.

현재 버전은 PDF 텍스트를 자동 추출해 보고서 JSON을 만든 뒤 기존 HWPX 템플릿에 반영합니다. PDF 양식별 세부 파싱은 실제 첨부 테스트 로그를 보며 계속 다듬습니다.

## 아직 보관/TODO 상태인 스킬

- `a10-new-quote`: Amaranth 10 신규 고객 견적서 생성
- `hwp-reader`: HWP/HWPX 읽기, 분석, 생성

## 웹 Codex로 기능 추가하기

`chatgpt.com/codex`에서 이 repo를 선택하고 이렇게 요청하면 됩니다.

```text
이 repo의 README와 skills/a10-new-quote/SKILL.md를 먼저 읽어줘.
GitHub Issue에 Amaranth10 견적 조건을 적으면 견적서 xlsx를 만들어주는 Actions 자동화를 추가해줘.
```

## 구조

```text
.github/
  ISSUE_TEMPLATE/
  workflows/
scripts/
  download_issue_attachment.py
  generate_wehago_quote.py
  extract_dm_emails.py
  build_maintenance_data.py
skills/
  a10-cover-sheet/
  a10-new-quote/
  douzone-dm-emaillist/
  douzone-maintenance-report/
  hwp-reader/
  pdf-seal-stamp/
  wehago-new-quote/
generated/
```

## 주의

- Issue에 첨부한 파일과 생성 결과는 repo에 commit될 수 있습니다. private repo 기준으로 운영하세요.
- 실제 고객 정보, 계약서, 견적 금액, 인감 이미지가 포함될 수 있으니 공개 repo로 전환하지 마세요.
- 결과물은 `generated/<기능명>/issue-번호/run-id/` 아래에 저장됩니다.
