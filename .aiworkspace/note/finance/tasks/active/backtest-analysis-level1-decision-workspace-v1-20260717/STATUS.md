# Status

Status: Design Review / 8차 Modifier-Free Multi-Select Controls
Last Updated: 2026-07-18

## Current Position

- [x] current Level1 code, docs, browser surface audit
- [x] visual companion을 사용한 UX 대안 비교
- [x] product scope와 사용자 수준 합의
- [x] single / Mix flow, result hierarchy, advanced settings 합의
- [x] development strategy, strategy catalog, saved Mix entry 합의
- [x] T2 pure read model + one-shell 접근 합의
- [x] product / state / result / responsive / test design 승인
- [x] approved design self-review
- [x] detailed implementation PLAN 작성
- [x] 1차 Truth / Handoff Contract
- [x] 2차 Decision Workspace Read Model
- [x] 3차 Single Strategy One-Shell
- [x] 4차 Portfolio Mix One-Shell
- [x] 5차 Runtime QA / Docs / Closeout
- [x] 6차 current settings flow / state / payload audit
- [x] 6차 corrective design 작성과 self-review
- [x] 6차 사용자 design review
- [x] 6차 implementation plan
- [x] 6차 RED -> GREEN implementation / Browser QA / closeout
- [x] 7차 all-strategy UI / renderer / runtime boundary audit
- [x] 7차 Schema-Driven React Settings 접근 사용자 승인
- [x] 7차 corrective design 작성과 self-review
- [x] 7차 written design 사용자 review
- [x] 7차 implementation plan
- [x] 7차 RED -> GREEN implementation / Browser QA / closeout
- [x] 8차 native multi-select root cause / option count audit
- [x] 8차 adaptive multi-select 접근 사용자 승인
- [x] 8차 corrective design 작성과 self-review
- [x] 8차 written design 사용자 review
- [x] 8차 implementation plan
- [ ] 8차 RED -> GREEN implementation / Browser QA / closeout

## Approved Roadmap

1. Level1 Truth / Handoff Contract
2. Level1 Decision Workspace Read Model
3. Single Strategy One-Shell
4. Portfolio Mix One-Shell
5. Runtime QA / Docs / Closeout
6. Single Strategy Settings Workspace Corrective
7. Unified React Strategy Settings Workspace
8. Modifier-Free Multi-Select Controls

## Current Corrective Position

- 1~5차 기능 / 판단 계약은 완료 상태를 유지한다.
- 사용자 Browser review에서 Single Strategy Step 2가 legacy form hierarchy와 중복
  Strategy / Variant picker를 유지한 implementation gap을 확인했다.
- 13개 strategy/variant form, React intent, session state, prefill, shared runner를
  감사하고 shared Python settings shell corrective design을 추가했다.
- 승인된 design을 PLAN Task 10~13으로 확장하고 같은 세션에서 inline
  executing-plans와 TDD로 순차 실행했다.
- Task 10~12에서 공통 settings shell, 선택 ownership, 전술 전략 6종과 strict
  factor 7개 variant의 설정 계층을 구현했다.
- Task 13 Browser QA에서 실제 Equal Weight와 Quality + Value Strict Annual 실행,
  Annual / Quarterly variant, fresh -> stale 보존, development Gate, desktop / 760px
  overflow를 확인하고 canonical docs를 동기화했다.

## Current 7차 Position

- 사용자 재검토에서 6차가 information hierarchy만 정렬하고 native Streamlit form을
  보존해 전략별 visual inconsistency가 남은 것을 확인했다.
- 9개 user choice / 13개 concrete renderer, actual GTAA DOM, React/Python intent,
  prefill / payload / runner 경계를 다시 감사했다.
- CSS reskin과 detail-only hybrid는 목표를 충족하지 못해 Python-owned schema와
  React settings surface를 결합한 C안을 승인했다.
- 7차 DESIGN은 6차에서 out-of-scope였던 full React editor를 범위 안으로 옮기되
  Python validation / payload / execution / Gate ownership을 유지한다.
- 사용자 승인 후 PLAN Task 14~20으로 pure schema, 전술·팩터 payload parity, Python
  intent/fallback, React settings, primary route cutover, Browser QA/docs closeout을 확정했다.
- Task 14~19에서 9개 user choice / 12개 primary concrete variant의 Python-owned schema,
  exact payload projection, validated intent, generic fallback, React 4-section editor와 primary
  route cutover를 완료했다. legacy Quality Snapshot/native renderer는 replay compatibility로만
  남겼다.
- Task 20 Browser QA에서 전체 9개 choice가 profile 1개, section 4개, CTA 1개를 공유함을
  확인했다. actual Equal Weight / GTAA / Quality+Value Annual 실행과 760px 단일 열·overflow
  0을 확인했고 QA 중 발견한 compatibility variant 노출과 hidden-field 실행 회귀를 각각
  RED -> GREEN으로 수정했다.

## Current 8차 Position

- 사용자 실제 사용 확인에서 native `<select multiple>`가 macOS Command / Windows·Linux
  Ctrl modifier를 요구해 기본 5개 선택도 단일 선택처럼 읽히는 interaction gap을 확인했다.
- Python schema와 payload는 이미 배열, 중복 금지, option allow-list를 지원하므로 runtime이나
  strategy contract가 아니라 공통 React `multi_select` renderer 문제로 범위를 고정했다.
- 옵션 수 20개 이하는 checkbox-card grid, 21개 이상은 검색·checkbox list·selected chip을
  쓰는 adaptive C안을 사용자 승인에 따라 DESIGN에 추가했다.
- 작성된 설계를 사용자 승인받았고 PLAN Task 21~22로 TDD 구현, Browser QA와 docs
  closeout을 확정했다.
