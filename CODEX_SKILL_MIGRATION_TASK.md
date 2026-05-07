# Codex 작업지시서 — Claude Skill → GitHub/Codex용 더존 산출물 자동화 도구 이관

## 0. 작업 배경

이 저장소는 기존에 Claude Skill로 만들어 둔 더존비즈온 기술영업 업무용 자동화 도구를 GitHub/Codex 기반으로 재구성하기 위한 저장소다.

목표는 단순히 `.skill` 파일을 보관하는 것이 아니라, 모바일/웹에서 ChatGPT 또는 GitHub Issue로 작업 요청을 남기면 Codex가 유지보수 가능한 Python CLI 도구로 실행·수정·테스트할 수 있게 만드는 것이다.

현재 이관 대상 Claude Skill은 다음과 같다.

| 우선순위 | Skill | 용도 | 현재 구성 | 이관 방향 |
|---:|---|---|---|---|
| 1 | 기존고객사 구매신청서 생성기 | 기존 고객 추가구매/유저추가/모듈추가 구매신청서 Excel 생성 | 이미 GitHub 업로드됨 | repo의 메인 기능으로 표준화 |
| 2 | `a10-new-quote` | Amaranth 10 신규 고객 가격확약서 생성 | `SKILL.md` + A10 Cloud/On-premise Excel 템플릿 | CLI 생성기 구현/보강 |
| 3 | `wehago-new-quote` | WEHAGO 신규 고객 견적서 생성 | `SKILL.md` + WEHAGO Excel 템플릿 | CLI 생성기 구현/보강 |
| 4 | `a10-cover-sheet` | Amaranth 10 견적서 갑지/가격제안서 요약 생성 | `SKILL.md` + `generate_cover.py` + 갑지 템플릿 | 기존 스크립트 CLI 표준화 |
| 5 | `pdf-seal-stamp` | PDF 계약서/공문 등에 인감 이미지 오버레이 | `SKILL.md` + `overlay_seal.py` + 도장 이미지 | 보안 주의하며 CLI 표준화 |
| 6 | `hwp-reader` | HWP/HWPX 읽기·분석·HWPX 생성 | `SKILL.md` + HWP/HWPX 파서/생성 스크립트 | 공통 유틸 패키지화 |
| 7 | `douzone-maintenance-report` | 월별 유지보수 내역서 HWPX 자동 생성 | `SKILL.md` + `generate_report.py` | HWPX 보고서 생성 모듈화 |
| 8 | `douzone-dm-emaillist` | DM 발송용 이메일 리스트/고객 구성 분석 | `SKILL.md` + pandas/openpyxl 스크립트 | Excel 분석 CLI 표준화 |

---

## 1. 최종 목표

### 1.1 사용자 관점 목표

외근 중 모바일에서 다음과 같은 요청이 가능해야 한다.

```text
서울AI재단 기존고객 구매신청서 만들어줘.
Amaranth 10 그룹웨어 100유저 추가, 월납 기준, 담당자는 이영진 대리야.
```

또는 GitHub Issue로 다음과 같은 작업지시를 남기면 Codex가 코드 수정/테스트/README 갱신까지 수행해야 한다.

```text
기존고객사 구매신청서 생성기에 YAML 입력 방식을 추가해줘.
샘플 입력으로 xlsx가 생성되는 smoke test도 붙여줘.
```

### 1.2 개발 관점 목표

- Claude Skill 구조를 그대로 보관하되, 실제 실행은 Python CLI로 통일한다.
- 모든 생성기는 YAML 또는 JSON 입력을 받을 수 있어야 한다.
- 모든 결과물은 `outputs/` 폴더에 생성한다.
- 실제 고객사 정보, 견적금액, 도장 이미지, 산출물은 commit하지 않는다.
- 샘플 데이터는 반드시 가상 고객사 기준으로 작성한다.
- 템플릿의 서식, 병합셀, 수식은 최대한 보존한다.
- 주요 기능별 smoke test를 작성한다.

---

## 2. 권장 repo 구조

아래 구조로 정리한다.

```text
douzone-quote-bot/
  README.md
  CODEX_SKILL_MIGRATION_TASK.md
  pyproject.toml
  requirements.txt
  .gitignore

  douzone_quote_bot/
    __init__.py
    cli.py
    common/
      __init__.py
      excel.py
      files.py
      validation.py
      pdf.py
      hwpx.py
    purchase_request/
      __init__.py
      generator.py
    a10_new_quote/
      __init__.py
      generator.py
      rules.py
    wehago_new_quote/
      __init__.py
      generator.py
      rules.py
    a10_cover_sheet/
      __init__.py
      generator.py
    pdf_seal_stamp/
      __init__.py
      overlay.py
    hwp_reader/
      __init__.py
      parse_hwp.py
      parse_hwpx.py
      generate_hwpx.py
    maintenance_report/
      __init__.py
      generator.py
    dm_emaillist/
      __init__.py
      build_dm_list.py
      build_product_analysis.py

  skills/
    purchase-request/
      SKILL.md
      templates/
      scripts/
    a10-new-quote/
      SKILL.md
      templates/
    wehago-new-quote/
      SKILL.md
      templates/
    a10-cover-sheet/
      SKILL.md
      assets/
      scripts/
    pdf-seal-stamp/
      SKILL.md
      assets/
      scripts/
    hwp-reader/
      SKILL.md
      assets/
      scripts/
    douzone-maintenance-report/
      SKILL.md
      scripts/
    douzone-dm-emaillist/
      SKILL.md
      scripts/

  samples/
    purchase_request.sample.yaml
    a10_cloud_quote.sample.yaml
    a10_onpremise_quote.sample.yaml
    wehago_company_quote.sample.yaml
    wehago_tax_quote.sample.yaml
    a10_cover_sheet.sample.yaml
    pdf_seal_stamp.sample.yaml
    maintenance_report.sample.json
    dm_emaillist.sample.yaml

  tests/
    test_purchase_request.py
    test_a10_new_quote.py
    test_wehago_new_quote.py
    test_a10_cover_sheet.py
    test_pdf_seal_stamp.py
    test_hwp_reader.py
    test_maintenance_report.py
    test_dm_emaillist.py

  outputs/
    .gitkeep
```

---

## 3. 공통 개발 규칙

### 3.1 CLI 명령 체계

아래와 같이 하나의 진입점으로 실행되게 만든다.

```bash
python -m douzone_quote_bot purchase-request --input samples/purchase_request.sample.yaml --output outputs/sample_purchase_request.xlsx
python -m douzone_quote_bot a10-new-quote --input samples/a10_cloud_quote.sample.yaml --output outputs/sample_a10_cloud.xlsx
python -m douzone_quote_bot wehago-new-quote --input samples/wehago_company_quote.sample.yaml --output outputs/sample_wehago.xlsx
python -m douzone_quote_bot a10-cover-sheet --input samples/a10_cover_sheet.sample.yaml --output outputs/sample_a10_cover
python -m douzone_quote_bot pdf-seal-stamp --input samples/pdf_seal_stamp.sample.yaml --output outputs/sample_stamped.pdf
python -m douzone_quote_bot maintenance-report --input samples/maintenance_report.sample.json --output outputs/sample_maintenance.hwpx
python -m douzone_quote_bot dm-emaillist --input samples/dm_emaillist.sample.yaml --output outputs/sample_dm_list.xlsx
```

### 3.2 입력 파일 규칙

- YAML 또는 JSON 입력을 지원한다.
- 필수값이 없으면 임의 생성하지 말고 명확한 에러를 반환한다.
- 고객사명, 사업자번호, 금액, 할인율, 납부방식은 실행 전후 로그로 검증한다.
- 날짜 기본값은 실행일 기준 `YYYYMMDD`로 처리하되, 입력값이 있으면 입력값을 우선한다.

### 3.3 Excel 처리 규칙

- `openpyxl.load_workbook(..., data_only=False)`를 기본으로 사용한다.
- 템플릿의 수식, 병합셀, 스타일, 시트 구조를 최대한 보존한다.
- 병합셀은 반드시 시작셀에만 값을 쓴다.
- 금액 계산식이 이미 템플릿에 있으면 수식 셀은 건드리지 않는다.
- Excel PDF 변환이 필요한 경우 LibreOffice headless 변환을 사용하되, 변환 실패 시 xlsx라도 생성하고 실패 사유를 명확히 출력한다.

### 3.4 보안/개인정보 규칙

다음 파일은 commit 금지한다.

```gitignore
outputs/
customer_files/
real_customer_inputs/
*.pdf
*_실제고객사*.xlsx
*_실제고객사*.hwpx
*.env
.DS_Store
__pycache__/
.pytest_cache/
```

도장 이미지(`douzone_seal.png`)는 민감 자산일 수 있으므로 다음 중 하나로 처리한다.

1. private repo에서만 관리한다.
2. repo에는 placeholder만 두고 실제 이미지는 runtime input으로 받는다.
3. 환경변수 또는 별도 비공개 경로로 지정한다.

Codex는 실제 고객정보가 포함된 산출물을 commit하면 안 된다.

---

## 4. Skill별 상세 작업지시

## 4.1 기존고객사 구매신청서 생성기

### 목적

기존 고객사의 유저 추가, 모듈 추가, 서비스 추가 건을 구매신청서 Excel로 생성한다.

### 요구사항

- 현재 GitHub에 업로드된 기존고객사 구매신청서 생성 기능을 repo의 최우선 기능으로 정리한다.
- YAML/JSON 입력을 받아 구매신청서 xlsx를 생성한다.
- 템플릿 서식, 병합셀, 수식은 보존한다.
- 고객사명, 제품명, 모듈, 수량, 납부방식, 담당자, 작성일자를 입력값으로 받는다.
- 누락값은 임의로 채우지 말고 에러 또는 `확인 필요`로 표시한다.

### 샘플 입력

```yaml
customer_name: 가상테스트주식회사
request_type: 기존고객 추가구매
product: Amaranth 10
payment_type: 월납
sales_owner: 이영진 대리
quote_date: 2026-05-07
items:
  - name: 그룹웨어 사용자
    quantity: 100
    unit: 유저
  - name: 전자결재
    quantity: 100
    unit: 유저
memo: 샘플 데이터입니다. 실제 고객정보가 아닙니다.
```

### 완료 기준

- `samples/purchase_request.sample.yaml`로 xlsx 생성 성공
- 생성 파일이 `outputs/`에 저장됨
- pytest smoke test 통과
- README에 모바일 요청 예시 추가

---

## 4.2 `a10-new-quote` — Amaranth 10 신규 고객 가격확약서

### 현재 Skill 요약

- 목적: Amaranth 10 최초 도입 고객 가격확약서 xlsx 초안 생성
- 지원 유형:
  - 구축형/설치형: `templates/a10_onpremise_template.xlsx`
  - 클라우드형: `templates/a10_cloud_template.xlsx`
- PDF 변환은 기본 범위에서 제외. xlsx 초안 생성이 우선이다.
- 할인율은 적용하지 않고 표준가 초안 생성이 기본이다.

### 필수 기능

- `quote_type`으로 `cloud` 또는 `onpremise`를 받는다.
- 고객사명, 전문가 유저수, 일반 사용자 수, 메일 유저수, 모듈 구성, 교육비 유형, 옵션을 입력받는다.
- 모듈 선행조건을 검증한다.
- A10 Cloud 템플릿은 확인된 셀 매핑을 사용한다.
- A10 On-premise 템플릿은 항목명 스캔 방식으로 수량 입력한다.

### 주요 룰

#### 모듈 선행조건

```text
예산관리 → 회계관리 선도입 필요
자산관리 → 예산관리 선도입 필요, 비영리 중심
외주관리 → 생산관리 선도입 필요
원가관리 → 생산관리 선도입 필요
UC확장팩 → ERP 모듈 1개 이상 필요
```

#### Cloud 템플릿 핵심 셀

| 항목 | 셀/행 | 처리 |
|---|---|---|
| 고객사명 | D5 | 병합셀 시작셀에 입력 |
| 견적담당 | D9 | 이영진 대리 기본값 |
| 영업센터 | J8 | TS영업2센터 강서2Unit 기본값 |
| 영업담당 | J9 | 이영진 대리 기본값 |
| 회계관리 | R25 J열 | 수량 입력 |
| 인사관리 | R31 J열 | 수량 입력 |
| 예산관리 | R37 J열 | 수량 입력 |
| 자산관리 | R45 J열 | 수량 입력 |
| 영업관리 | R46 J열 | 수량 입력 |
| 구매자재관리 | R48 J열 | 수량 입력 |
| 생산관리 | R49 J열 | 수량 입력 |
| 외주관리 | R50 J열 | 수량 입력 |
| 원가관리 | R51 J열 | 수량 입력 |
| UC 확장팩 | R55 J열 | 수량 입력 |
| UC 단독팩 | R56 J열 | 수량 입력 |
| 전문가 유저 사용료 | R121 J열 | 수량 입력 |
| 사용자 유저 사용료 | R122 J열 | 수량 입력 |
| 메일 유저 사용료 | R123 J열 | 수량 입력 |
| 스토리지 요금제 | R124 J열 | 수량 입력 |
| SSL 인증서 | R142 I열 | 수식 대신 직접값 500000 입력 |

### 샘플 입력

```yaml
quote_type: cloud
customer_name: 가상복지재단
sales_owner: 이영진 대리
sales_center: TS영업2센터 강서2Unit
expert_users: 10
employee_users: 100
mail_users: 100
modules:
  accounting: 1
  hr: 1
  budget: 1
  uc_extension: 1
education:
  type: FoEX
  nonprofit: true
options:
  ssl: basic
  storage_sets: 1
  one_ai_plan: null
```

### 완료 기준

- Cloud 샘플 입력으로 xlsx 생성 성공
- On-premise 샘플 입력으로 xlsx 생성 성공
- 모듈 선행조건 위반 시 명확한 에러 출력
- SSL R142 I열 수식 오류 방지 처리 완료
- README에 A10 신규 견적 사용법 추가

---

## 4.3 `wehago-new-quote` — WEHAGO 신규 고객 견적서

### 현재 Skill 요약

- 목적: WEHAGO 최초 도입 고객 견적서 자동 생성
- 지원 유형:
  - 신규 기업: `신규(기업)` 시트
  - 세무: `세무` 시트
- 출력: xlsx + pdf
- 템플릿: `templates/wehago_template.xlsx`

### 필수 기능

- `quote_type`으로 `company` 또는 `tax`를 받는다.
- 신규 기업은 Smart A 10 모듈, WEHAGO 사용료, 요금제, 납부기준, 그룹웨어 부가서비스를 입력받는다.
- 세무는 WEHAGO T 유저수, 타임머신, ONE AI, Smart A 2.0 수량, 유저추가 수량을 입력받는다.
- PDF 변환 시 사용하지 않는 시트는 제거하고 필요한 직접값을 먼저 입력한다.
- PDF에 `#NAME?`, `#REF!`가 없는지 검증한다.

### 신규 기업 주요 셀

| 항목 | 셀/행 | 처리 |
|---|---|---|
| 고객사명 | G7 | 직접 입력 |
| 납부기준 | H29 | `(월납)` 또는 `(연납)` |
| 요금제 유형 | C32 | `CLUB 요금제` 또는 `PRO 요금제` |
| 회계관리 | M21 | 수량 입력 |
| 인사급여 | M22 | 수량 입력 |
| 물류관리 | M23 | 수량 입력 |
| 법인조정 | M24 | 수량 입력 |
| 개인조정 | M25 | 수량 입력 |
| Smart A 2.0 | M26 | 수량 입력 |
| Smart A 10 사용료 | M31 | 유저수 입력 |
| 요금제 기본 | M32 | EA 수 입력 |
| 요금제 사용료 | M33 | 유저수 입력 |
| ONE AI | M41 | 개월수 입력 |
| 법정의무교육 4종 | M42 | 유저수 입력 |
| 법정의무교육 5종 | M43 | 유저수 입력 |
| 회사저장공간 | M44 | GB/TB 입력 |
| 전자결재 | M47 | 유저수 입력 |
| 근태관리 | M48 | 유저수 입력 |
| CRM | M49 | 유저수 입력 |
| PMS | M50 | 유저수 입력 |

### PDF 변환 시 직접값 대체

```text
U12 = 010-4903-2311
U13 = nofr2311@douzone.com
```

### 샘플 입력

```yaml
quote_type: company
customer_name: 가상테스트기업
payment_type: monthly
plan_type: CLUB
smart_a10:
  accounting: 5
  hr_payroll: 5
  logistics: 0
  corporate_tax: 0
  personal_tax: 0
  smart_a_2: 0
wehago:
  smart_a10_usage_users: 5
  plan_base_qty: 1
  plan_usage_users: 20
addons:
  one_ai_months: 0
  legal_training_4_users: 0
  legal_training_5_users: 0
  storage: 0
  approval_users: 20
  attendance_users: 20
  crm_users: 0
  pms_users: 0
```

### 완료 기준

- 신규 기업 샘플 xlsx + pdf 생성 성공
- 세무 샘플 xlsx + pdf 생성 성공
- PDF 텍스트 검증 시 `#NAME?`, `#REF!` 없음
- README에 WEHAGO 신규 견적 사용법 추가

---

## 4.4 `a10-cover-sheet` — Amaranth 10 갑지/가격제안서 요약

### 현재 Skill 요약

- 목적: Amaranth 10 견적서의 갑지 데이터를 읽어 PDF + XLSX 생성
- 입력: xlsx 또는 pdf
- 출력: `<basename>.pdf` + `<basename>.xlsx`
- 기존 스크립트: `scripts/generate_cover.py`
- 템플릿: `assets/galji_template.xlsx`

### 필수 기능

- 기존 `generate_cover.py`를 `douzone_quote_bot/a10_cover_sheet/generator.py`로 이관한다.
- CLI에서 input 파일과 output basename을 받는다.
- xlsx 입력 시 갑지 시트에서 필요한 값을 읽는다.
- pdf 입력 시 가능한 범위에서 pdfplumber로 파싱한다.
- 데이터 없는 유형 열은 자동 숨김 처리한다.
- 값 없는 항목 행은 자동 숨김 처리한다.
- 출력은 xlsx + pdf를 모두 생성한다.

### 기본 제안사 정보

```text
사업자번호: 134-81-08473
회사명: 주식회사 더존비즈온
주소: 강원도 춘천시 남산면 버들1길 130
대표이사: 이강수, 지용구
영업담당: 이영진 대리
연락처: 010-4903-2311
견적번호: 생략
```

### 완료 기준

- 샘플 xlsx 입력으로 갑지 xlsx + pdf 생성 성공
- 숨김 열/행 로직 동작
- LibreOffice PDF 변환 실패 시 에러 메시지 명확화
- README에 갑지 생성 사용법 추가

---

## 4.5 `pdf-seal-stamp` — PDF 인감/도장 오버레이

### 현재 Skill 요약

- 목적: PDF 문서 지정 위치에 인감 이미지를 반투명 오버레이
- 기존 스크립트: `scripts/overlay_seal.py`
- 기본 도장 이미지: `assets/douzone_seal.png`
- 위치, 페이지, 크기, 투명도 파라미터 지원

### 필수 기능

- CLI에서 원본 PDF, 출력 PDF, 도장 이미지, page, x, y, size, alpha를 받는다.
- 도장 이미지가 없으면 명확한 에러를 출력한다.
- 기본 도장 이미지는 민감 자산으로 간주하고 commit 여부를 확인한다.
- 가능하면 placeholder 도장으로 테스트한다.
- 원본 PDF는 수정하지 않는다.

### 기본 파라미터

```yaml
page: 2
x: 493
y: 100
size: 58
alpha: 180
```

### 샘플 입력

```yaml
input_pdf: samples/sample_contract.pdf
seal_image: samples/sample_seal_placeholder.png
page: 2
x: 493
y: 100
size: 58
alpha: 180
```

### 완료 기준

- 샘플 PDF에 placeholder 도장 오버레이 성공
- 결과 PDF가 `outputs/`에 생성됨
- 실제 법인인감 이미지가 공개 repo에 commit되지 않도록 보호
- README에 위치 조정 방법 추가

---

## 4.6 `hwp-reader` — HWP/HWPX 읽기·분석·생성 공통 유틸

### 현재 Skill 요약

- 목적: HWP/HWPX 읽기, 표 추출, HWPX 생성, 템플릿 기반 치환
- 기존 스크립트:
  - `read_hwp.py`
  - `parse_hwp.py`
  - `parse_hwpx.py`
  - `generate_hwpx.py`
- 내장 양식:
  - `assets/report-full.hwpx`
  - `assets/report-summary.hwpx`

### 필수 기능

- HWP/HWPX 자동 감지 기능 유지
- 텍스트 추출, 표 추출, JSON 출력 옵션 유지
- HWPX 생성 기능을 `maintenance-report`에서도 재사용 가능하게 모듈화
- 암호화된 파일, 이미지/OLE 객체, 복잡한 병합셀 등 제한사항을 README에 명시

### CLI 예시

```bash
python -m douzone_quote_bot hwp-read --input samples/sample.hwpx --json outputs/sample_hwpx.json
python -m douzone_quote_bot hwpx-generate --input samples/hwpx_content.sample.json --template report-summary --output outputs/sample_report.hwpx
```

### 완료 기준

- 샘플 HWPX에서 텍스트 추출 성공
- 샘플 JSON으로 HWPX 생성 성공
- `maintenance-report`가 이 유틸을 재사용할 수 있도록 import 구조 정리

---

## 4.7 `douzone-maintenance-report` — 월별 유지보수 내역서 HWPX 생성

### 현재 Skill 요약

- 목적: 이전 달 HWPX 양식을 템플릿으로 삼아 당월 온라인/유선 상담 내역을 반영한 유지보수 내역서 생성
- 기존 스크립트: `scripts/generate_report.py`
- 입력: 이전 달 HWPX + 온라인상담 PDF 추출 데이터 + 유선상담 PDF 추출 데이터
- 출력: 새 월의 HWPX 파일

### 필수 기능

- PDF 자체 파싱은 1차 범위에서 제외하고, 구조화된 JSON 입력을 받아 HWPX 생성하는 CLI부터 만든다.
- 입력 JSON에는 `year`, `prev_month`, `month`, `report_date`, `online`, `phone` 배열을 포함한다.
- XML 특수문자 이스케이프, rowCnt 업데이트, 월 교체 로직을 유지한다.
- 템플릿 HWPX의 기존 바이너리/이미지를 보존한다.

### 샘플 입력

```json
{
  "year": "2026",
  "prev_month": "04월",
  "month": "05월",
  "report_date": "2026-05-07 (목)",
  "online": [
    {
      "date": "2026-05-02",
      "title": "샘플 온라인 문의",
      "question": "샘플 문의 내용입니다.",
      "answer": "샘플 답변 내용입니다."
    }
  ],
  "phone": [
    {
      "no": "1",
      "date": "2026.05.03",
      "gubun": "아웃바운드",
      "content": "샘플 상담 내용입니다.",
      "answer": "샘플 답변 내용입니다.",
      "category": "기타"
    }
  ]
}
```

### 완료 기준

- 샘플 JSON + 샘플 HWPX 템플릿으로 HWPX 생성 성공
- 생성 HWPX가 zip 구조로 열림
- README에 PDF 원문 추출은 수동/추후 범위임을 명시

---

## 4.8 `douzone-dm-emaillist` — DM 이메일 리스트/고객 구성 분석

### 현재 Skill 요약

- 목적: Upgrade 리스트, NSM 고객현황, 재계약 리스트를 기준으로 이메일 보완 및 DM 발송용 Excel 생성
- 기존 스크립트:
  - `scripts/build_dm_list.py`
  - `scripts/build_product_analysis.py`
- 모드:
  - Mode A: DM 이메일 리스트 생성
  - Mode B: 고객 구성 비율 + 솔루션 고객 이메일 추출

### 필수 기능

- 업로드 파일 조합을 보고 모드를 자동 판별하거나, CLI에서 mode를 지정할 수 있게 한다.
- 사업자번호는 하이픈 제거 후 매칭한다.
- 이메일 우선순위는 기존 Skill 규칙을 유지한다.

### 이메일 우선순위

```text
1순위: Upgrade 파일 원본 이메일
2순위: NSM 담당자이메일
3순위: 재계약 담당자 이메일
미확보: 빈칸 유지, 출처='미확보'
```

### 출력 컬럼

```text
상호명
사업자번호
이메일
이메일 (복사용)
이메일출처
```

### 완료 기준

- 샘플 Excel 2~3개로 DM 리스트 생성 성공
- 고객 구성 비율 분석 파일 생성 성공
- 99개 단위 색상 그룹 로직 유지
- README에 입력 파일 판별 기준 추가

---

## 5. README에 반드시 포함할 내용

README에는 다음 내용을 포함한다.

### 5.1 설치 방법

```bash
git clone <repo-url>
cd douzone-quote-bot
python -m venv .venv
source .venv/bin/activate  # Windows는 .venv\Scripts\activate
pip install -r requirements.txt
```

### 5.2 사용 예시

```bash
python -m douzone_quote_bot purchase-request --input samples/purchase_request.sample.yaml --output outputs/sample_purchase_request.xlsx
python -m douzone_quote_bot a10-new-quote --input samples/a10_cloud_quote.sample.yaml --output outputs/sample_a10_cloud.xlsx
python -m douzone_quote_bot wehago-new-quote --input samples/wehago_company_quote.sample.yaml --output outputs/sample_wehago.xlsx
```

### 5.3 모바일에서 ChatGPT/Codex에 요청하는 예시

```text
이 repo 기준으로 기존고객사 구매신청서 생성기를 수정해줘.
입력값은 samples/purchase_request.sample.yaml 구조로 받고,
출력은 outputs/고객사명_구매신청서_YYYYMMDD.xlsx로 만들어줘.
샘플 테스트와 README 사용법도 같이 갱신해줘.
```

```text
A10 신규 견적 생성 기능을 구현해줘.
quote_type이 cloud면 a10_cloud_template.xlsx를 쓰고,
onpremise면 a10_onpremise_template.xlsx를 쓰게 해줘.
모듈 선행조건 검증과 샘플 YAML도 추가해줘.
```

### 5.4 주의사항

- 이 repo는 private repo 기준으로 운영한다.
- 실제 고객사 산출물은 commit하지 않는다.
- 공개 repo로 전환할 경우 템플릿, 도장 이미지, 가격정보를 제거한다.
- Excel/PDF/HWPX 생성 결과는 반드시 최종 검수 후 고객에게 전달한다.

---

## 6. 테스트 요구사항

pytest 기준 smoke test를 우선 작성한다.

### 최소 테스트

```bash
pytest -q
```

테스트 범위는 다음과 같다.

| 테스트 | 검증 내용 |
|---|---|
| `test_purchase_request.py` | 샘플 입력으로 xlsx 생성 여부 |
| `test_a10_new_quote.py` | Cloud/On-premise 샘플 xlsx 생성 여부 |
| `test_wehago_new_quote.py` | 신규기업/세무 샘플 xlsx 생성 여부 |
| `test_a10_cover_sheet.py` | 샘플 입력으로 xlsx 생성 여부 |
| `test_pdf_seal_stamp.py` | 샘플 PDF에 placeholder 도장 오버레이 여부 |
| `test_hwp_reader.py` | 샘플 HWPX 텍스트 추출/생성 여부 |
| `test_maintenance_report.py` | 샘플 JSON으로 HWPX 생성 여부 |
| `test_dm_emaillist.py` | 샘플 Excel로 DM 리스트 생성 여부 |

PDF 변환이나 LibreOffice 의존 기능은 CI 환경에서 실패할 수 있으므로, 우선 optional test로 분리한다.

---

## 7. requirements.txt 후보

아래 패키지를 우선 사용한다.

```text
openpyxl
pandas
PyYAML
pypdf
pdfplumber
reportlab
Pillow
lxml
pytest
```

LibreOffice는 Python 패키지가 아니므로 README에 별도 설치 요구사항으로 기재한다.

---

## 8. Codex 작업 순서

Codex는 아래 순서대로 작업한다.

### Phase 1 — repo 정리

1. 현재 repo 파일 구조 확인
2. 기존 Claude Skill 파일을 `skills/` 아래로 정리
3. `.gitignore` 보강
4. `requirements.txt`, `pyproject.toml` 정리
5. README 초안 작성

### Phase 2 — 기존고객사 구매신청서 우선 표준화

1. 현재 업로드된 구매신청서 생성 코드를 분석
2. YAML/JSON 입력 방식 추가
3. CLI 명령 추가
4. 샘플 입력 추가
5. smoke test 추가

### Phase 3 — 견적 생성기 이관

1. `a10-new-quote` generator 구현
2. `wehago-new-quote` generator 구현
3. 템플릿 셀 매핑 적용
4. 샘플 입력과 테스트 추가

### Phase 4 — 보조 도구 이관

1. `a10-cover-sheet` 기존 스크립트 이관
2. `pdf-seal-stamp` 기존 스크립트 이관
3. `hwp-reader` 유틸 이관
4. `maintenance-report` 생성기 이관
5. `dm-emaillist` 분석기 이관

### Phase 5 — 문서화/검증

1. README 전체 사용법 정리
2. 모바일 GitHub Issue 요청 예시 추가
3. pytest 실행
4. 생성 산출물이 `.gitignore`에 의해 commit되지 않는지 확인

---

## 9. Codex에게 지켜야 할 제한사항

- 실제 고객사명, 사업자번호, 견적금액, 계약서, 도장 이미지가 포함된 파일은 commit하지 않는다.
- 샘플은 `가상테스트기업`, `가상복지재단`, `샘플고객사` 등 가상 데이터만 사용한다.
- 템플릿 파일이 private repo에 포함되어 있을 경우 해당 템플릿은 수정하지 않고 복사본으로 작업한다.
- 기존 수식 셀을 직접값으로 덮어쓰지 않는다. 단, Skill에서 명시한 오류 방지용 셀은 예외다.
- 기능 구현이 불완전한 경우 README에 현재 제한사항을 명확히 남긴다.
- 실패한 테스트가 있으면 숨기지 말고 원인과 다음 조치를 PR/Issue에 적는다.

---

## 10. 이번 Issue의 완료 기준

이번 작업은 전체 자동화를 한 번에 완성하는 것이 아니라, Claude Skill을 Codex가 유지보수할 수 있는 repo 구조로 전환하는 1차 작업이다.

완료 기준은 다음과 같다.

- [ ] `skills/` 아래에 각 Claude Skill 원본이 정리되어 있다.
- [ ] `douzone_quote_bot/` 패키지 구조가 만들어져 있다.
- [ ] 공통 CLI 진입점이 있다.
- [ ] 기존고객사 구매신청서 생성기가 YAML/JSON 입력으로 실행된다.
- [ ] 최소 1개 이상의 샘플 입력으로 xlsx 생성 테스트가 통과한다.
- [ ] `outputs/` 및 실제 고객자료가 `.gitignore` 처리되어 있다.
- [ ] README에 설치법, 사용법, 모바일 요청 예시가 있다.
- [ ] A10/WEHAGO/갑지/PDF도장/HWP/DM 스킬의 이관 계획이 문서화되어 있다.

---

## 11. Codex에게 바로 전달할 요약 프롬프트

아래 문구를 GitHub Issue 본문 또는 Codex 작업 요청에 그대로 사용할 수 있다.

```text
이 repo는 Claude Skill로 만들어 둔 더존비즈온 기술영업 산출물 자동화 도구를 GitHub/Codex 기반 Python CLI 도구로 이관하기 위한 repo야.

첨부/업로드된 skill 파일과 이 CODEX_SKILL_MIGRATION_TASK.md를 기준으로 작업해줘.

우선순위는 다음이야.
1. 기존고객사 구매신청서 생성기 표준화
2. a10-new-quote 이관
3. wehago-new-quote 이관
4. a10-cover-sheet 이관
5. pdf-seal-stamp 이관
6. hwp-reader, maintenance-report, dm-emaillist 이관

이번 1차 작업에서는 전체를 완성하려고 하지 말고,
repo 구조 정리 + 공통 CLI + 기존고객사 구매신청서 YAML 입력 실행 + smoke test + README 갱신까지 해줘.

실제 고객정보, 도장 이미지, 산출물은 commit하지 말고, 샘플은 가상 데이터만 사용해.
실행 결과와 남은 작업은 README 또는 PR 설명에 정리해줘.
```
