# Yame Skills

Claude에서 쓰던 더존 업무 자동화 스킬을 GitHub 웹/모바일에서 실행할 수 있게 옮기는 repo입니다.

가격표 기반 구매신청서/견적 자동화는 별도 repo에서 관리합니다.

- https://github.com/nofr2311-rgb/douzone-quote-bot

이 repo는 그 외 작업, 예를 들면 PDF 인장 찍기, Amaranth 10 갑지 생성, WEHAGO/A10 신규 견적 템플릿 이관 같은 작업을 담당합니다.

## 지금 바로 쓸 수 있는 기능

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

## 앞으로 붙일 스킬

아래 스킬들은 원본 `SKILL.md`, 기존 스크립트, 템플릿을 `skills/` 아래에 보존했습니다.

- `a10-new-quote`: Amaranth 10 신규 고객 견적서 생성
- `wehago-new-quote`: WEHAGO 신규 고객 견적서 생성
- `a10-cover-sheet`: Amaranth 10 갑지 생성
- `pdf-seal-stamp`: PDF 인장/직인 오버레이
- `hwp-reader`: HWP/HWPX 읽기, 분석, 생성
- `douzone-maintenance-report`: 더존 유지보수 이력표 HWPX 생성
- `douzone-dm-emaillist`: DM 발송용 이메일 리스트 분석

## 웹 Codex로 기능 추가하기

`chatgpt.com/codex`에서 이 repo를 선택하고 이렇게 요청하면 됩니다.

```text
이 repo의 README와 skills/wehago-new-quote/SKILL.md를 먼저 읽어줘.
WEHAGO 신규 견적서 생성 기능을 GitHub Issue 첨부/입력으로 실행할 수 있게 만들어줘.
완료되면 모바일에서 Issue만 만들어도 결과 xlsx를 받을 수 있어야 해.
```

또는:

```text
skills/a10-new-quote를 참고해서
GitHub Issue에 Amaranth10 견적 조건을 적으면 견적서 xlsx를 만들어주는 Actions 자동화를 추가해줘.
```

## 구조

```text
.github/
  ISSUE_TEMPLATE/
  workflows/
scripts/
  download_issue_attachment.py
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
