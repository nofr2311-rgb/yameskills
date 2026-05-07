# Yame Skills

Claude에서 사용하던 업무 자동화 Skill 자료 중, 구매신청서 생성기를 제외한 나머지 스킬을 보관하는 repo입니다.

구매신청서 CLI 작업은 별도 repo에서 관리합니다.

- https://github.com/nofr2311-rgb/douzone-quote-bot

## 포함된 스킬

- `a10-new-quote`: Amaranth 10 신규 고객 견적서 생성
- `wehago-new-quote`: WEHAGO 신규 고객 견적서 생성
- `a10-cover-sheet`: Amaranth 10 갈지/가격제안서 요약
- `pdf-seal-stamp`: PDF 인감/직인 오버레이
- `hwp-reader`: HWP/HWPX 읽기, 분석, 생성 유틸리티
- `douzone-maintenance-report`: 더존 유지보수 이력표 HWPX 생성
- `douzone-dm-emaillist`: DM 발송용 이메일 리스트 및 고객 구성 분석

## 구조

```text
skills/
  a10-new-quote/
    SKILL.md
    TODO.md
    templates/
  wehago-new-quote/
    SKILL.md
    TODO.md
    templates/
  a10-cover-sheet/
    SKILL.md
    TODO.md
    scripts/
    assets/
  pdf-seal-stamp/
    SKILL.md
    TODO.md
    scripts/
    assets/
  hwp-reader/
    SKILL.md
    TODO.md
    scripts/
    assets/
  douzone-maintenance-report/
    SKILL.md
    TODO.md
    scripts/
  douzone-dm-emaillist/
    SKILL.md
    TODO.md
    scripts/
```

## 현재 상태

각 폴더에는 Claude Skill에서 추출한 `SKILL.md`, 기존 스크립트, 템플릿, 자산을 보존했습니다. `TODO.md`에는 Codex/GitHub 기반 CLI로 이관할 때 필요한 후속 작업을 정리했습니다.

아직 이 repo 자체는 통합 Python CLI 패키지가 아닙니다. 실제 실행형 CLI 구현은 스킬별로 별도 작업하면서 추가할 예정입니다.

## 주의

- 실제 고객 정보, 계약서, 견적 산출물은 commit하지 않습니다.
- `customer_files/`, `real_customer_inputs/`, `.env`, PDF 산출물, 실제 고객사명 포함 산출물은 `.gitignore`로 제외합니다.
- `pdf-seal-stamp`의 `douzone_seal.png`는 요청에 따라 repo에 포함했습니다. 공개 범위 변경 전에는 민감 자산 여부를 다시 확인하세요.
