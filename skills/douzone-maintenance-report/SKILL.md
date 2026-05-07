---
name: douzone-maintenance-report
description: >
  더존비즈온 고객사 월별 유지보수 내역서 HWPX 자동 생성 스킬.
  이전 달 HWPX 파일을 템플릿으로 삼아 양식/폰트/스타일을 100% 보존한 채,
  당월 온라인상담·유선상담 PDF 내용을 읽어 새 HWPX를 만든다.

  트리거: "유지보수 내역서", "유지보수 보고서", "이번 달 유지보수", "유지보수 hwpx",
  "유지보수 한글", "고객지원 현황 hwpx", "매월 유지보수 문서", "유지보수 작업결과서".
  이전 달 .hwpx 파일 + 온라인/유선 상담 PDF 파일이 업로드되면 반드시 이 스킬을 사용한다.
---

# 더존비즈온 유지보수 내역서 HWPX 생성 스킬

## 개요

매월 반복되는 유지보수 내역서 작성을 자동화한다.
- **템플릿**: 이전 달 HWPX → 양식/폰트/스타일 100% 그대로 유지
- **교체 내용**: 월·날짜 텍스트 + 온라인 문의 전체 + 유선상담 전체
- **출력**: 새 월의 HWPX 파일

---

## 입력 파일 확인

사용자가 업로드해야 하는 파일:

| 파일 | 설명 |
|------|------|
| `*_02월*.hwpx` (이전 달) | 양식 템플릿 (필수) |
| `*온라인상담*고객지원현황*3월*.pdf` | 당월 온라인 문의 내역 |
| `*유선상담*고객지원현황*3월*.pdf` | 당월 유선 상담 내역 |

파일이 부족하면 어떤 파일이 빠졌는지 안내하고 업로드를 요청한다.

---

## 실행 워크플로우

### STEP 1 — 파일 확인

```
/mnt/user-data/uploads/ 에서 파일 목록 확인
- .hwpx 파일 → 템플릿 경로 저장
- 온라인상담 PDF → online_pdf 경로 저장
- 유선상담 PDF → phone_pdf 경로 저장
```

### STEP 2 — PDF에서 데이터 추출

PDF는 이미 컨텍스트에 문서 블록으로 제공된다.
Claude가 직접 읽어서 아래 JSON 구조로 추출한다.

**온라인 문의 항목** (`online` 배열):
```json
{
  "date": "2026-03-03",
  "title": "문서 발송 시, 정부기준코드 오류 건",
  "question": "문의내용 전문 (줄바꿈 없이 한 문자열)",
  "answer": "답변내용 전문 (줄바꿈 없이 한 문자열)"
}
```

**유선상담 항목** (`phone` 배열):
```json
{
  "no": "1",
  "date": "2026.03.04",
  "gubun": "아웃바운드",
  "content": "상담내용 전문",
  "answer": "답변내용 전문",
  "category": "접속장애"
}
```

> **주의**: 문의내용·답변내용은 PDF 원문 전체를 그대로 넣는다. 요약하거나 생략하지 않는다.
> 줄바꿈(\n)은 공백으로 대체한다 (스크립트가 처리).

### STEP 3 — 메타 정보 결정

템플릿 HWPX 파일명과 PDF에서 다음 값을 확인한다:

```json
{
  "year": "2026",
  "prev_month": "02월",     ← 템플릿(이전 달)의 월
  "month": "03월",          ← 당월
  "report_date": "2026-04-08 (수)"   ← 오늘 날짜(작성일)
}
```

### STEP 4 — JSON 파일 저장

```python
import json
data = {
    "year": "2026",
    "prev_month": "02월",
    "month": "03월",
    "report_date": "2026-04-08 (수)",
    "online": [ ... ],   # STEP 2에서 추출
    "phone":  [ ... ],
}
with open('/home/claude/report_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
```

### STEP 5 — 스크립트 실행

```bash
SKILL_DIR="<이 스킬의 경로>"
cp "$SKILL_DIR/scripts/generate_report.py" /home/claude/

python3 /home/claude/generate_report.py \
  --template "/mnt/user-data/uploads/<이전달_파일명>.hwpx" \
  --data     "/home/claude/report_data.json" \
  --output   "/mnt/user-data/outputs/<고객사명>_2026년_유지보수_내역서_26년_<월>월.hwpx"
```

### STEP 6 — 파일 제공

`present_files` 도구로 결과 HWPX를 사용자에게 전달한다.

---

## 출력 파일명 규칙

```
{고객사명}_2026년_유지보수_내역서_26년_{MM}월.hwpx
예) 북한이탈주민재단_2026년_유지보수_내역서_26년_03월.hwpx
```

---

## PDF 파싱 가이드

### 온라인 상담 PDF 포맷

각 행: `순번 | 등록번호 | 등록일자 | 제품 | 제목 | 요청내용 | 답변내용`

- `등록일자` → `date` (YYYY-MM-DD)
- `제목` → `title`
- `요청내용` (문의 내용 첫 ✔ 문의 내용: 이후 텍스트) → `question`
- `답변내용` ([답변내용] 이후 텍스트, 인사말/공지사항 제외) → `answer`

**답변 정제**: "[공지사항]Amaranth10 유튜브..." 이후는 제거한다.

### 유선 상담 PDF 포맷

각 행: `번호 | 제품 | 날짜 | 구분 | 상담내용 | 답변내용 | 상담유형`

- `번호` → `no`
- `날짜` (YYYY.MM.DD) → `date`
- `구분` (아웃바운드/인바운드) → `gubun`
- `상담내용` → `content`
- `답변내용` → `answer`
- `상담유형` → `category`

---

## 주의사항

1. **XML 특수문자**: `&`, `<`, `>`, `"` → 스크립트가 자동 이스케이프
2. **줄바꿈**: 셀 내 `\n`은 공백으로 대체 (한글 HWPX 셀은 단락 분리 불가)
3. **월 교체 조건**: `prev_month`가 실제 템플릿 내부 텍스트와 일치해야 교체됨
   - 불일치 시 스크립트가 경고 없이 교체를 건너뜀 → 수동 확인 필요
4. **추가 AS**: 내역이 없으면 그대로 "별도 처리 내용 없음" 유지
5. **파일 손상 방지**: 스크립트는 원본 HWPX의 모든 바이너리(이미지 등)를 그대로 복사

---

## 스크립트 위치

`scripts/generate_report.py`

**핵심 함수**:
- `generate(template_path, data, output_path)` — 메인 생성 함수
- `make_inquiry_table(tbl_id, date, title, question, answer)` — 온라인 문의 표 XML 생성
- `make_phone_tr(row_idx, cols)` — 유선상담 데이터 행 XML 생성
- `esc(text)` — XML 이스케이프

---

## 자주 발생하는 문제

| 증상 | 원인 | 해결 |
|------|------|------|
| 파일 손상 | XML 조립 오류 | lxml로 유효성 검사 후 저장 |
| 월 미교체 | prev_month 불일치 | 템플릿 내부 텍스트 직접 확인 |
| 표 깨짐 | 셀 내 특수문자 미이스케이프 | esc() 함수 적용 확인 |
| 유선상담 행 수 오류 | rowCnt 미업데이트 | re.sub으로 rowCnt 교체 확인 |
