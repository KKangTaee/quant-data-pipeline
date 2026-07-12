# Notes

## 2026-07-11 Initial Audit

- 현재 registry 6개 후보의 `세부 audit에서 연결`은 저장된 module audit의 non-PASS row를 최대 3개 연결한 상태다.
- `기간 미포함`은 후보 기간이 2016년 이후라 2000~2009 stress window가 포함되지 않은 결과이며 freshness 문제가 아니다.
- 빈 관측은 Tax / Account 정성 판단, strategy-specific perturbation NOT_RUN, provider row의 criteria 계약 공백으로 나뉜다.
- weighted mix 2개에는 holdings / exposure와 source map 보강 대상이 있으나 단일 후보는 stale-only provider snapshot이라 기존 missing-only collection plan에 잡히지 않는다.

## 2026-07-11 Action Taxonomy

- `기간 미포함`은 `period_outside`, parameter perturbation `NOT_RUN`은 `implementation_gap`으로 분리했다.
- provider freshness / operability / holdings / exposure는 `refreshable_data`, lifecycle / delisting은 `source_discovery`로 분리했다.
- 측정된 성과·집중·상관 REVIEW는 `inherited_limit`, Tax / Account는 `user_decision`으로 분리했다.

## 2026-07-11 Data Enrichment Handoff

- provider collection plan은 누락 symbol뿐 아니라 operability provenance의 stale symbol도 수집 대상으로 포함한다.
- Final Review CTA는 실행 가능한 provider plan이 있을 때만 노출되고, React는 navigation intent만 전달한다.
- 같은 selection source와 saved validation을 Practical Validation으로 전달하며 실제 수집은 Level2 Python service가 수행한다.
- 수집 후 저장된 검토서는 자동 변경하지 않고 Flow 2 재검증, 새 결과 저장, Final Review 재확인을 요구한다.

## 2026-07-11 Browser QA Findings

- raw audit id와 score policy code는 첫 화면에서 한국어 의미로 바꾸고, source / 기준일은 접힌 상세 근거로 유지했다.
- `기간 미포함`은 데이터 최신화 문제가 아니라 검증 범위 문제이며, `모멘텀 기간 변경 검증`의 미실행은 수집이 아니라 검증 기능 보강 문제로 표시한다.
- 세금 / 계좌 조건은 자동 감점이나 수집 대상이 아니라 사용자가 판단 사유에 남길 항목이다.
- lifecycle / delisting 근거는 current snapshot 새로고침만으로 해결되지 않으므로 historical source 탐색으로 분리한다.
