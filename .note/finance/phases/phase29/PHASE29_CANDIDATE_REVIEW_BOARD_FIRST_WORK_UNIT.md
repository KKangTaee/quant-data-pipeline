# Phase 29 Candidate Review Board First Work Unit

## 이 문서는 무엇인가

Phase 29의 첫 번째 작업 단위 기록이다.
`Backtest > Candidate Review` 패널을 추가해 current candidate registry를
후보 검토 보드로 읽게 만든 내용을 정리한다.

## 쉽게 말하면

기존에는 후보가 registry, compare quick re-entry, Pre-Live Review에 흩어져 있었다.
이번 작업은 그 앞에 "후보를 먼저 읽는 화면"을 만든 것이다.

## 왜 필요한가

후보를 바로 compare로 보내거나 Pre-Live로 저장하면,
사용자는 이 후보가 current anchor인지, near miss인지, 단순 scenario인지 먼저 확인하기 어렵다.

Candidate Review Board는 후보를 투자 추천으로 확정하지 않고,
다음 검토 행동을 정하는 중간 화면이다.

## 구현한 것

1. `Backtest` panel에 `Candidate Review`를 추가했다.
2. active current candidate registry row를 summary metric과 표로 보여준다.
3. `Candidate Board`에서 후보별 다음 정보를 보여준다.
   - Review Stage
   - Family
   - Role
   - CAGR / MDD
   - Promotion / Shortlist / Deployment
   - Why It Exists
   - Suggested Next Step
4. `Inspect Candidate`에서 후보 1개를 자세히 보고 Pre-Live Review로 넘길 수 있게 했다.
5. `Send To Compare`에서 기존 current candidate re-entry를 다시 사용할 수 있게 했다.
6. `Pre-Live Review`로 넘어갈 때 아직 저장된 것이 아니라는 안내를 보여준다.

## 중요한 경계

- Candidate Review는 live trading approval이 아니다.
- `Suggested Next Step`은 투자 추천이 아니라 다음 검토 행동 제안이다.
- Pre-Live Review로 넘겨도 바로 저장되지 않는다.
- 실제 저장은 Pre-Live 화면에서 operator reason / next action을 확인한 뒤 `Save Pre-Live Record`로 한다.

## 수정한 코드

- `app/web/pages/backtest.py`

## 검증

- `python3 -m py_compile app/web/pages/backtest.py`
- `python3 plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py validate`

## 다음 작업

다음 작업은 `Latest Backtest Run` 또는 `History` 결과를 candidate review 초안으로 넘기는 흐름을 검토하는 것이다.
이 작업은 자동 투자 추천이 아니라, 사용자가 의미 있는 결과를 후보 기록으로 남길 때 필요한 handoff를 만드는 것이다.
