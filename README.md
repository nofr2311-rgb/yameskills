# Douzone Quote Bot

Claude Skill로 관리하던 더존 업무 산출물 자동화 자료를 Codex/GitHub에서 유지보수 가능한 Python CLI 구조로 이관하는 저장소입니다.

## 현재 1차 지원 범위

- 기존고객사 구매신청서 생성: YAML/JSON 입력으로 `.xlsx` 생성
- 나머지 Claude Skill: `skills/` 아래에 원본 스킬 자료를 정리하고 TODO 상태로 보존

## 설치

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

macOS/Linux에서는 가상환경 활성화 명령만 `source .venv/bin/activate`를 사용하면 됩니다.

## 구매신청서 생성

```bash
python -m douzone_quote_bot purchase-request --input samples/purchase_request.sample.yaml --output outputs/sample_purchase_request.xlsx
```

JSON 입력도 사용할 수 있습니다.

```bash
python -m douzone_quote_bot purchase-request --input samples/purchase_request.sample.json --output outputs/sample_purchase_request.xlsx
```

`--output`을 생략하면 `outputs/` 아래에 `고객사명_purchase_request_YYYYMMDD.xlsx` 형식으로 생성합니다.

## 입력 예시

```yaml
customer_name: 가상테스트주식회사
request_type: 기존고객 추가구매
product: Amaranth 10
payment_type: 월납
sales_owner: 홍길동 매니저
quote_date: 2026-05-07
items:
  - name: 그룹웨어 사용자
    quantity: 100
    unit: 유저
memo: 샘플 데이터입니다. 실제 고객정보가 아닙니다.
```

단가나 금액처럼 입력에서 확정되지 않은 값은 임의로 채우지 않고 `확인 필요`로 표시합니다.

## 테스트

```bash
pytest -q
```

현재 smoke test는 샘플 YAML로 구매신청서 `.xlsx`가 생성되는지만 확인합니다.

## 모바일/Issue 요청 예시

```text
이 repo 기준으로 기존고객사 구매신청서 생성기를 수정해주세요.
입력값은 samples/purchase_request.sample.yaml 구조로 받고,
출력은 outputs/고객사명_purchase_request_YYYYMMDD.xlsx로 만들어주세요.
샘플 테스트와 README 사용법도 같이 갱신해주세요.
```

## 주의사항

- `outputs/`는 `.gitignore`에 포함되어 실제 산출물이 commit되지 않도록 했습니다.
- 실제 고객정보, 계약서, 견적 금액, 법인 인감 이미지는 샘플이나 commit 대상에 포함하지 마세요.
- 공개 repo로 전환할 경우 템플릿과 인감 이미지에 민감 정보가 없는지 별도 검토가 필요합니다.
- A10/WEHAGO/갈지/PDF 인감/HWP/DM 기능은 이번 1차 작업에서 구조 보존과 TODO 정리까지만 진행했습니다.
