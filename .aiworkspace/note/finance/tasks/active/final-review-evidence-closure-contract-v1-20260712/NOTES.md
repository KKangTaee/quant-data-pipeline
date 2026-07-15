# Notes

## 2026-07-12 User Intent

- `남은 판단 근거`는 단순 참고 목록이 아니라 각 항목을 실제 workflow에서 종결할 수 있어야 한다.
- Level3는 검증 실행 단계가 아니지만, 인수한 한계를 수용·보류하거나 Monitoring으로 이관하는 판단 장치는 필요하다.
- 현재 세션은 설계와 실행 계획을 확정하고, 실제 구현은 같은 worktree / branch의 새 세션에서 수행한다.

## 2026-07-12 Confirmed Findings

- latest GRS replay는 실행됐지만 requested `2026-07-10` 대비 actual `2026-05-29`로 42일 gap이 남았다.
- BIL의 6월 마지막 row는 `2026-06-26`, 나머지 GRS risky ticker는 `2026-06-30`이다.
- GRS month-end exact-date alignment는 6월 공통 row를 잃고 `2026-05-29`에서 끝난다.
- `latest_replay`에는 Final Review trace adapter가 없어 stored provenance가 있어도 `missing_contract`가 된다.
- latest replay와 PIT price audit가 같은 period gap을 중복 설명한다.
- universe/listing과 survivorship audit도 같은 historical lifecycle root를 중복 설명한다.
- current role mapping은 latest replay와 data coverage에 각각 고정 `-6`을 적용한다.
- pre-final enrichment gate는 current provider collector가 실행 가능한 operability / holdings-exposure / macro만 blocker로 포함한다.
- latest user validation append로 `PRACTICAL_VALIDATION_RESULTS.jsonl`이 변경돼 있으며 이 task에서 stage / rewrite하지 않는다.

## Design Decision

- 해결 가능한 문제는 Level2에서 닫고, 해결 불가능한 핵심 문제는 block/defer한다.
- 비핵심 residual만 accepted limit 또는 Monitoring transfer로 Final Review에 전달한다.
- 완료 조건은 evidence count zero가 아니라 open terminal-state count zero다.

## 2026-07-12 Planning Session Findings

- 현재 `latest_replay`는 required module이지만 `_FINAL_REVIEW_TRACE_SOURCES` adapter가 없어 stored provenance가 있어도 `missing_contract`로 떨어진다.
- `data_coverage`의 `PIT price window coverage`가 같은 runtime/period status를 다시 읽고 두 module 모두 `pv_data_caution` 고정 `-6` 대상이 된다.
- `build_practical_validation_recheck_plan()`은 source universe 공통 최신일이 아니라 `load_latest_market_date()` 전체 DB max를 requested end로 사용한다.
- GRS는 `filter_by_period() -> align_dates()` exact intersection으로 ticker별 6월 마지막 거래일 차이를 제거하며 valuation-only row contract가 없다.
- focused baseline은 `unittest` 75개가 통과했다. 이 worktree `.venv`에는 `pytest`가 설치되어 있지 않다.

## 2026-07-12 Implementation Decisions

- `backtest_evidence_closure_v1`은 replay/PIT와 universe/survivorship derived check를 각각 하나의 root issue로 합친다.
- 등록된 Python replay handler만 `resolve_now` CTA가 될 수 있다. handler가 없으면 `engineering_required`로 정규화하고 승격을 차단한다.
- static manual universe의 사후 선택 한계는 비핵심 `accepted_limit`, dynamic historical universe의 PIT membership/delisting 부재는 critical `engineering_required`다.
- GRS는 signal row와 latest-common valuation row를 분리한다. current DB 기준 요청일 `2026-07-10`, 공통일 `2026-06-26`, 마지막 signal `2026-05-29`, valuation `2026-06-26`이다.
- Final Review decision row는 같은 validation의 `evidence_closure_snapshot`을 저장한다. accepted / monitoring_transferred / deferred / blocked는 기존 route와 operator reason에서 파생한다.
- role 고정 -6/-4 감점은 제거했다. 숫자 score effect는 root issue에 numeric observed/threshold와 명시적 effect가 있을 때만 적용하고, missing/open/critical은 Gate로 처리한다.

## 2026-07-12 Follow-up UX Decision

- Flow 4의 `근거 종결 경로`는 internal closure contract와 category criteria를 동시에 노출해 같은 문제를 반복했다.
- accepted-limit 항목은 Practical Validation에서 사용자가 해결할 action이 아니므로 큰 카드 목록과 `미정` 표시를 제거했다.
- Python은 accepted-limit root issue를 dedup해 `final_review_limit_count`만 workspace summary에 전달한다.
- Flow 3 React는 이 개수와 즉시 해결·개발 blocker 유무를 기존 summary band에서 표시하고, 상세 terminal 판단은 Final Review에 남긴다.
