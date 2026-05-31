# Validation Efficacy Hardening V1

Status: Implementation complete
Started: 2026-05-28

## 이걸 하는 이유?

현재 흐름은 Practical Validation과 Final Review를 거치지만, 사용자가 지적한 것처럼 검증 효력이 충분한지 별도로 한눈에 확인하기 어렵다.

첫 단계는 새 데이터를 저장하는 것이 아니라, 기존 validation evidence를 읽어 `point-in-time`, `look-ahead`, `survivorship`, `benchmark parity`, `data freshness`, `NOT_RUN` 위험을 별도 audit board로 노출하는 것이다.

## Scope

- Streamlit-free validation efficacy audit read model 추가
- Practical Validation result / Final Review evidence가 같은 audit summary를 읽도록 연결
- `NOT_RUN`, stale, proxy, benchmark mismatch, missing runtime replay를 pass로 숨기지 않음
- 저장 경계 명시: DB write / JSONL write / memo / preset / approval / order 없음

## Non-Goals

- 새 provider 수집
- DB schema 변경
- 새로운 JSONL registry 추가
- broker approval / order / rebalance
- 모든 strategy-specific sensitivity runtime sweep 구현

## Exit Criteria

- audit read model 테스트 통과
- Practical Validation / Final Review 표시 연결
- 저장 경계와 다음 후속 작업 문서화

## Implemented Slice

- `app/services/backtest_validation_efficacy.py`
  - Practical Validation result의 기존 compact evidence를 읽어 `PASS / REVIEW / NEEDS_INPUT / BLOCKED` audit row를 만든다.
  - runtime replay, runtime period coverage, benchmark parity, provider freshness, robustness, PIT / look-ahead, survivorship / universe, execution / storage boundary를 분리해 표시한다.
- `app/services/backtest_practical_validation_diagnostics.py`
  - 새 검증 결과에 top-level `validation_efficacy_audit`와 `validation_efficacy_display_rows`를 붙인다.
  - 별도 registry / DB write / user memo 저장은 추가하지 않는다.
- `app/services/backtest_evidence_read_model.py`
  - Final Review investability packet과 saved decision evidence rows가 같은 audit을 읽는다.
- `app/web/backtest_practical_validation.py`, `app/web/backtest_final_review.py`
  - Practical Validation과 Final Review에 compact audit board를 표시한다.
