# Design

## Stage Boundary

| Stage | Question | Blocks |
|---|---|---|
| Practical Validation | 검증 근거가 계산됐고 Final Review로 보낼 수 있는가? | 필수 module `BLOCKED / NEEDS_INPUT / NOT_RUN` |
| Final Review Selection | 이 후보를 선정 후보로 기록해 Dashboard에서 추적할 만큼 thesis / 역할 / 리스크 / follow-up 조건이 명확한가? | selection hard blockers |
| Selected Portfolio Dashboard | 선정 당시 thesis와 조건이 현재도 유지되는가? | read-only recheck / signal breach |
| Live / Deployment Readiness | 실제 돈을 넣어도 되는가? | capital, liquidity, cost, order, tax/account, approval blockers |

## Selection Gate Matrix

Final Review selection gate는 `BLOCKED / NEEDS_INPUT / NOT_RUN`을 우선 차단한다. `REVIEW`는 기본적으로 `open_review_items`로 보존하고 저장을 허용한다.

Selection 저장 차단 항목:

- runtime replay 미실행 / 실패
- benchmark / comparator parity 불일치
- 가격 coverage 실질 부족
- look-ahead / survivorship 위험이 `NEEDS_INPUT / BLOCKED`
- gross-only 또는 net/cost 적용 여부가 `NEEDS_INPUT / BLOCKED`
- weighted mix의 component 역할 / 비중 이유가 `NEEDS_INPUT / BLOCKED`
- Final Review evidence route 미준비
- execution boundary 위반

Selection 저장 가능하되 open review로 남길 항목:

- provider snapshot partial / stale
- construction concentration / overlap / exposure review
- risk contribution concentration / correlation review
- walk-forward / OOS / regime 성과 약화 review
- tax/account scope 미정
- cost / slippage sensitivity 추가 확인 필요
- liquidity / operability가 proxy 또는 partial evidence

## Policy Snapshots

- `selection_gate_policy_snapshot`: Final Review 저장 여부를 판단한다.
- `deployment_readiness_policy_snapshot`: 기존 엄격한 policy를 보존해 향후 Live / Deployment Readiness에서 재사용한다.
- `gate_policy_snapshot`: backward compatibility로 selection policy를 가리킨다.
- `open_review_items`: selection은 허용하지만 Dashboard / Live readiness에서 이어서 봐야 할 compact issue list.

## Evidence Mapping

Weighted mix source 변환은 component-level `weight_reason`, role source, 그리고 mix-level cost / turnover / net-cost evidence를 보존해야 한다.
