---
name: hwp-reader
description: >
  Read, extract text, and analyze HWP and HWPX (한글/한컴오피스) documents.
  Also generate new HWPX documents from templates.
  Use this skill whenever the user uploads or mentions a .hwp or .hwpx file,
  or asks to read/analyze/summarize a 한글 document. Also trigger when you detect
  a file in /mnt/user-data/uploads/ with .hwp or .hwpx extension, even if the
  user doesn't explicitly say "HWP". Common triggers: "이 한글 파일 읽어줘",
  "hwp 문서 분석해줘", "hwpx 내용 요약해줘", "한글 파일에서 표 추출해줘",
  "이 파일 뭐야" (when file is .hwp/.hwpx), uploading any .hwp/.hwpx file,
  "한글 문서 만들어줘", "hwpx로 보고서 작성해줘", "한글 파일로 저장해줘".
  Do NOT use for .doc, .docx, .pdf, or other non-HWP formats.
---

# HWP/HWPX 통합 스킬 — 읽기 + 생성

## 개요

한글(HWP/HWPX) 문서를 읽고, 분석하고, 새로 생성하는 통합 스킬.
외부 패키지 없이 Python 표준 라이브러리 + lxml만으로 동작한다.

## 기능 요약

| 기능 | HWP (바이너리) | HWPX (XML) |
|------|:-:|:-:|
| 텍스트 추출 | ✅ | ✅ |
| 표 추출 | ✅ | ✅ |
| 문서 분석/요약 | ✅ | ✅ |
| 문서 생성 | ❌ | ✅ |
| 템플릿 기반 치환 | ❌ | ✅ |

---

## 워크플로우 1: 읽기/분석

### 사용법

```bash
SKILL_DIR="<이 스킬의 경로>"
cp -r "$SKILL_DIR/scripts/" /home/claude/hwp-scripts/

# 자동 감지 (HWP/HWPX 구분 자동)
python3 /home/claude/hwp-scripts/read_hwp.py "/mnt/user-data/uploads/파일명.hwp"

# 표만 추출
python3 /home/claude/hwp-scripts/read_hwp.py "파일.hwpx" --tables-only

# JSON 출력
python3 /home/claude/hwp-scripts/read_hwp.py "파일.hwp" --json
```

### 지원 형식

| 형식 | 구조 | 파싱 방식 |
|------|------|-----------|
| HWP | OLE2 바이너리 | struct + zlib 직접 파싱 |
| HWPX | ZIP + XML (OWPML) | zipfile + xml.etree 파싱 |

---

## 워크플로우 2: HWPX 문서 생성

### 핵심 원리

한컴오피스 한글에서 만든 실제 양식의 뼈대(header.xml, version.xml 등)를
그대로 보존하고, **section0.xml만 새로 작성**한다.
이 방식이 XML을 처음부터 작성하는 것보다 호환성이 압도적으로 높다.

### 내장 양식

| 양식 | 파일 | 용도 |
|------|------|------|
| report-full | `assets/report-full.hwpx` | 보고서 기본 (다중 페이지) |
| report-summary | `assets/report-summary.hwpx` | 보고서 요약 (1페이지) |

### CLI 사용법

```bash
# 데모 문서 생성
python3 "$SKILL_DIR/scripts/generate_hwpx.py" \
  --template report-summary \
  --output result.hwpx \
  --demo

# JSON으로 내용 정의
python3 "$SKILL_DIR/scripts/generate_hwpx.py" \
  --template report-summary \
  --json content.json \
  --output result.hwpx

# 사용자 업로드 양식 사용
python3 "$SKILL_DIR/scripts/generate_hwpx.py" \
  --template-path "/mnt/user-data/uploads/사용자양식.hwpx" \
  --json content.json \
  --output result.hwpx
```

### Python API 사용법

```python
import sys
sys.path.insert(0, "/home/claude/hwp-scripts")
from generate_hwpx import generate_hwpx

content = [
    {"type": "heading", "text": "제목"},
    {"type": "empty"},
    {"type": "body", "text": "가. 본문 내용"},
    {"type": "table", "rows": [
        ["항목", "내용"],
        ["A", "B"],
    ]},
]

generate_hwpx(
    template_path="assets/report-summary.hwpx",
    content_elements=content,
    output_path="/mnt/user-data/outputs/result.hwpx"
)
```

### Content Element 타입

| type | 필수 필드 | 선택 필드 | 설명 |
|------|-----------|-----------|------|
| heading | text | charPr, paraPr, styleID | 제목 (기본: charPr=7, paraPr=25) |
| body | text | charPr, paraPr, styleID | 본문 들여쓰기 (기본: charPr=14, paraPr=26) |
| paragraph | text | charPr, paraPr, styleID | 일반 문단 (기본: 모두 0) |
| empty | - | paraPr | 빈 줄 |
| table | rows | col_widths, header_charPr, body_charPr, row_height | 표 |

### 양식 치환 (기존 HWPX 수정)

```python
from generate_hwpx import zip_replace

zip_replace("원본.hwpx", "결과.hwpx", {
    "OOO 신사업 보고서": "ERP 도입 제안서",
    "OOOO부서": "기술영업팀",
    "2022.12.31.": "2026. 3. 17.",
})
```

---

## 스타일 ID 참고 (report-summary 양식 기준)

### charPrIDRef (글자 스타일)

| ID | 설명 |
|----|------|
| 0 | 기본 10pt |
| 7 | 소제목용 볼드 |
| 8 | 부서/날짜용 |
| 9 | 표 헤더 볼드 |
| 14 | 본문 들여쓰기용 |
| 16 | 대제목 18pt 볼드 |

### paraPrIDRef (문단 스타일)

| ID | 설명 |
|----|------|
| 0 | 기본 (양쪽정렬) |
| 20 | 우측정렬 |
| 21 | 가운데정렬 |
| 22 | 양쪽정렬 (표 셀용) |
| 25 | 소제목 |
| 26 | 본문 들여쓰기 |

---

## 스크립트 요약

| 스크립트 | 역할 |
|----------|------|
| `scripts/read_hwp.py` | 메인 읽기 (HWP/HWPX 자동 감지) |
| `scripts/parse_hwpx.py` | HWPX 파서 |
| `scripts/parse_hwp.py` | HWP 바이너리 파서 |
| `scripts/generate_hwpx.py` | HWPX 생성기 (v4, 양식 기반) |

## 제한사항

- 암호화된 HWP/HWPX 읽기 불가
- 이미지/OLE 객체 추출 불가
- 복잡한 병합 셀 표는 불완전할 수 있음
- HWP → HWPX 변환 불가 (한글에서 다시 저장 필요)
- HWPX 생성 시 lxml 필요 (`pip install lxml --break-system-packages`)
