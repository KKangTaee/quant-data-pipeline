# Overview Market Movers EOD Refresh Scope

## 이걸 하는 이유?

`Workspace > Overview > 변동 종목`에서 Top1000 이상 / weekly 이상 기간의 `가격 이력 갱신`이 반복 실행 후에도 길게 잡히는 문제를 해결한다. 화면은 최신 유효 EOD 기준으로 정상 계산되는데, 갱신 action은 로컬 오늘 날짜와 다른 universe 기준을 사용해 이미 화면이 쓰는 종목까지 stale로 분류할 수 있었다.

## 1차

- 목적: provider fetch 전에 수집 대상, 범위, 시작일 이유를 계산하는 preflight 모델을 만든다.
- 범위: `app/jobs/overview_actions.py`, 관련 service contract tests.
- 완료 조건: selected/current/stale/repair/missing count와 range driver가 result details에 남는다.

## 2차

- 목적: `자료정상`이 화면 계산 정상과 가격 이력 갱신 필요를 섞지 않게 분리한다.
- 범위: `app/web/overview/market_movers_helpers.py`.
- 완료 조건: React payload의 trust panel과 summary가 refresh debt를 보조 근거로 노출한다.

## 3차

- 목적: 버튼 클릭 전 갱신 범위와 start date 이유를 사용자가 볼 수 있게 한다.
- 범위: Market Movers React payload / action metadata / Streamlit fallback caption.
- 완료 조건: non-daily 액션에 preflight summary가 포함되고 `as_of_date`가 action plan에 전달된다.

## 4차

- 목적: 실제 수집 실행이 다음 실행에서 짧아지도록 universe/as-of/batch 산정을 바로잡는다.
- 범위: EOD refresh action facade.
- 완료 조건: Top universe는 materialized liquidity universe를 쓰고, 화면 effective end date를 as-of로 받으며, stale/repair는 start date별 batch로 나뉜다.

## Verification

- Targeted service contract tests.
- `py_compile` for touched Python modules.
- Browser QA if the Streamlit surface can be loaded in this worktree.
