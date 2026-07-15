# Institutional Portfolios Workspace V1 Plan

Status: Active
Started: 2026-07-08

## 이걸 하는 이유?

Market Movers는 선택된 급등락 종목의 관심 근거를 보는 화면이고, 사용자가 요청한 새 기능은 투자 대가 / 기관별 전체 13F 포트폴리오와 분기별 보유 변화 자체를 탐색하는 별도 제품 흐름이다.
같은 화면에 섞으면 "현재 급등락 종목의 근거"와 "분기 지연된 기관 보유 공시"가 신호처럼 오해될 수 있으므로 `Workspace > Institutional Portfolios`로 분리한다.

## Goal

SEC Form 13F 공식 데이터셋을 DB-backed ingestion / loader / service read model로 연결하고, Finance Streamlit app의 Workspace에 `Institutional Portfolios` 탐색 화면을 추가한다.

## Scope

- 1차: 화면 IA와 read model contract 고정.
- 2차: SEC 13F official data set 기반 schema / parser / ingestion job / loader 추가.
- 3차: 기관별 최신 포트폴리오 MVP.
- 4차: 특정 종목 또는 CUSIP reverse lookup.
- 5차: 이전 분기 대비 변화와 섹터 / 산업 노출 요약.
- 6차: 문서, runbook, focused tests, Browser QA, commit.

## Out Of Scope

- 추천 종목 생성.
- 매수 / 매도 신호.
- 실시간 보유 변화 표현.
- broker order, live approval, auto rebalance 연결.
- Dataroma / WhaleWisdom / Fintel / Quiver 같은 제3자 유료 또는 약관 리스크 source를 ingestion 전제로 사용.
- CUSIP-symbol mapping을 완전하다고 가정하는 구현.

## Completion Conditions

- UI render path가 외부 provider를 직접 fetch하지 않는다.
- SEC 13F 수집은 `finance/data/* -> DB -> finance/loaders/* -> app/services/* -> app/web/*` 경계를 따른다.
- 13F 지연, 45일 제출 기한, short / derivative / hedge visibility 한계, CUSIP-symbol mapping 한계를 visible caveat로 둔다.
- Focused tests, py_compile, `git diff --check`, Browser QA를 가능한 범위에서 실행한다.
- generated artifact는 commit하지 않는다.
