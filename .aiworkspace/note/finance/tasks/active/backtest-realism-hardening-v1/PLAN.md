# Backtest Realism Hardening V1

Status: Implementation complete
Started: 2026-05-28

## 이걸 하는 이유?

검증 효력 audit은 gate에 연결됐지만, 백테스트 결과 자체가 실제 투자 환경의 비용, turnover, liquidity, benchmark-relative net performance, 세금 / 계좌 제약을 얼마나 반영했는지는 아직 한눈에 보기 어렵다.

이번 첫 slice는 core strategy runtime을 즉시 바꾸지 않고, 기존 result metadata와 Practical Validation evidence를 읽어 실전성 공백을 표시하는 read-only audit을 추가한다.

## Scope

- Streamlit-free Backtest Realism Audit read model 추가
- Practical Validation result에 compact realism audit 연결
- Practical Validation / Final Review / final decision evidence가 같은 audit을 읽도록 연결
- 거래비용, turnover, provider operability / liquidity, net performance policy, rebalance cadence, tax/account scope, execution boundary를 분리 표시
- 새 DB write, 새 JSONL registry, user memo, preset, approval, order, auto rebalance 없음

## Non-Goals

- core strategy cost model 변경
- 새 provider ingestion
- tax optimizer / broker integration
- actual account holding 자동 연결
- Backtest Realism Audit gate policy 연결

## Exit Criteria

- audit read model tests 통과
- Practical Validation / Final Review 표시 연결
- 기존 service contract 통과
- 저장 경계 문서화

## Implemented Slice

- `app/services/backtest_realism_audit.py`
  - 기존 validation result / source metadata / provider operability / diagnostic evidence를 읽어 Backtest Realism Audit을 만든다.
  - 거래비용, turnover, liquidity / operability, net performance policy, rebalance / trade timing, tax / account scope, execution boundary를 분리한다.
- `app/services/backtest_practical_validation_diagnostics.py`
  - 새 Practical Validation result에 `backtest_realism_audit`와 display rows를 붙인다.
- `app/services/backtest_evidence_read_model.py`
  - Investability packet과 saved final decision evidence rows가 Backtest Realism Audit을 읽는다.
- `app/web/backtest_practical_validation.py`, `app/web/backtest_final_review.py`
  - Practical Validation과 Final Review에서 audit board를 표시한다.
