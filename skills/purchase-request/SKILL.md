# 기존고객사 구매신청서 생성

## 상태

1차 이관에서 우선 CLI 실행이 가능하도록 정리한 Codex용 스킬입니다.

## 목적

기존 고객사의 추가 구매, 유저 추가, 모듈 추가 요청을 YAML 또는 JSON 입력으로 받아 구매신청서 Excel 파일을 생성합니다.

## 실행

```bash
python -m douzone_quote_bot purchase-request --input samples/purchase_request.sample.yaml --output outputs/sample_purchase_request.xlsx
```

`--output`을 생략하면 `outputs/` 아래에 고객사명과 작성일자를 사용한 파일명이 자동으로 생성됩니다.

## 입력 필드

- `customer_name`: 고객사명
- `request_type`: 신청 구분
- `product`: 제품명
- `payment_type`: 납부 방식
- `sales_owner`: 영업 담당자
- `quote_date`: 작성일자. 생략 시 실행일 기준
- `writer`: 작성자. 생략 시 `sales_owner`
- `items`: 구매 항목 배열
- `memo`: 비고

금액, 단가처럼 확정되지 않은 값은 임의로 채우지 않고 `확인 필요`로 표시합니다.
