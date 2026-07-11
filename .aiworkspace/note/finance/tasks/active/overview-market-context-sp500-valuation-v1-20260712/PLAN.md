# Overview Market Context S&P 500 Valuation V1 Plan

Status: Design Approved In Conversation
Last Updated: 2026-07-12

## 이걸 하는 이유?

현재 `Workspace > Overview > Market Context`는 마지막 거래일 움직임, 시장 브리프, 섹터 압력, 이벤트와 자료 보강 흐름을 함께 보여준다. 사용자는 이 화면을 제거하고, S&P 500의 실제 실적과 FOMC SEP 경제전망을 바탕으로 현재 시장이 최근 멀티플 및 예상 실적 대비 어느 구간에 있는지 수치와 그래프로 판단하고자 한다.

## Goal

기존 Market Context UI를 제거하고 React 기반의 두 가치평가 그래프로 교체한다.

1. 최근 5년 월별 후행 PER의 log-normal 평균·표준편차 구간
2. 현재 TTM 실제 EPS와 FOMC SEP 성장 시나리오를 이용한 예상 EPS 및 S&P 500 지수 밴드

## Scope

- Shiller 월별 S&P 가격·EPS 데이터 수집 및 저장
- S&P Index Earnings 실제 EPS snapshot 입력·저장 경계
- FOMC SEP 최신 release 탐색, GDP/PCE projection vintage 수집 및 저장
- SPX·SPY 가격과 동일 기준일 정렬
- 최근 60개월 후행 PER, log(PER) 평균·표준편차, Z-score 계산
- 보수·기준·낙관 FOMC 예상 EPS와 SPX band, SPY 환산 band 계산
- 기존 Market Context visible UI 제거
- 신규 React Streamlit component 기반 화면 구현
- 단위·서비스·컴포넌트·브라우저 QA
- task/root/docs alignment 및 단계별 coherent commit

## Out Of Scope

- live trading, 주문, 자동 리밸런싱, 투자 승인 signal
- LSEG I/B/E/S 또는 FactSet 유료 consensus 연동
- 현재 구성 종목 EDGAR 합산을 통한 공식 S&P 500 지수 EPS 자체 복제
- Market Movers, Futures Macro, Sentiment, Events 탭 재설계
- 기존 Market Context 하위 서비스의 즉시 대량 삭제
- raw job, 저장 rows, 운영 진단 패널을 새 Market Context 주 화면에 노출

## Development Roadmap

### 1차: Source Contract And Persistence

- Shiller, S&P Index Earnings, FOMC SEP, SPX/SPY source contract와 DB schema를 구현한다.
- 발표일, 기준일, actual/estimate, as-reported/operating, vintage를 보존한다.
- 완료 조건: UI 직접 fetch 없이 DB-backed loader가 canonical rows를 반환한다.

### 2차: Five-Year Multiple Engine

- 최근 60개 완결 월의 후행 PER와 log(PER) 평균·표준편차를 계산한다.
- 5년을 공식 판정 기준으로 사용하고 3년은 기간 민감도 검증에만 사용한다.
- 완료 조건: 현재 PER, Z-score, 구간, 기간 민감도 결과가 deterministic test로 재현된다.

### 3차: FOMC Earnings And Index Scenario Engine

- 최신 FOMC SEP median/central tendency를 이용해 예상 성장률과 EPS 시나리오를 만든다.
- 예상 EPS와 5년 멀티플을 결합해 SPX band 및 SPY 환산 band를 계산한다.
- 완료 조건: 입력 기준일, 계산식, scenario label, 괴리율이 service contract에 포함된다.

### 4차: React Market Context Replacement

- 기존 Market Context 브리프·섹터·이벤트·자료 보강 visible UI를 제거한다.
- React component로 두 그래프와 핵심 수치, 근거일, 한계 disclosure를 렌더링한다.
- 완료 조건: Market Context 첫 화면은 두 가치평가 질문에 답하고 운영 진단 UI를 노출하지 않는다.

### 5차: PIT Hardening, QA, Documentation

- 실제/추정 혼합, stale source, 부족 history, non-positive EPS, 기준일 불일치를 방어한다.
- Python/React test, build, Browser QA, screenshot, docs sync를 완료한다.
- 완료 조건: 관련 검증이 통과하고 사용자-facing QA screenshot과 durable handoff가 남는다.

## Stop Condition

- 다섯 차수가 모두 완료되고 관련 QA가 통과한다.
- 기존 Market Context visible UI가 제거되고 React 가치평가 화면으로 교체된다.
- 각 차수 또는 coherent implementation unit이 커밋된다.
- 실행하지 못한 검증과 남은 데이터 라이선스·PIT 한계가 명시된다.
