# Futures Macro Pattern Outlook V1 Plan

Status: Design Review
Started: 2026-07-18

## Goal

`Workspace > Overview > Futures Macro`를 오늘의 위험과 단순 1D / 1W / 1M 변화율을 나열하는 화면에서,
현재 다중 기간 패턴과 향후 5 / 20거래일 위험 체제의 조건부 방향을 함께 읽는 단기 거시 레이더로 개선한다.

## 이걸 하는 이유?

현재 화면은 오늘 위험과 그 근거를 잘 설명하지만, 최근 1일·1주·1개월 흐름 사이의 지속·반전·확산 관계를 설명하지 않는다.
기존 과거 점검도 과거의 1일 시나리오 라벨만 묶으므로 사용자가 원한 "현재 며칠 또는 몇 주간의 패턴 이후 무엇이 더 자주 발생했는가"를 답하지 못한다.

선물 매크로는 장기 경기예측기가 아니라 장중·일간 재가격화와 향후 1~4주 위험 체제 전이를 확인하는 화면으로 정의한다.
월 단위 구조 국면은 경제사이클이 소유하고, 선물 매크로는 더 빠른 시장 반응과 조건부 단기 전망을 소유한다.

## Approved Product Direction

- 첫 결과는 개별 자산 매수·매도 확률이 아니라 `전체 시장 위험 체제`다.
- 자산별 주식·금리·달러·안전자산·원자재 결과는 체제 판단의 근거와 보조 분포로 둔다.
- 현재 관측 기간은 1D 충격, 5D 단기 흐름, 20D 월간 체제를 결합한다.
- 전망 기간은 다음 5D와 20D다. 다음 1D 전망은 오늘 위험 브리프와 중복되고 잡음이 커 V1 주 결과에서 제외한다.
- 방향 확률은 무조건 기준 확률과 함께 보여주고, 검증 우위가 없으면 `방향 우위 미확인`으로 표시한다.
- live approval, broker order, 자동 매매, backtest / Practical Validation gate 연결은 하지 않는다.

## Scope

### In Scope

- 다중 기간 macro feature / pattern state read model
- 현재 패턴의 지속·반전·확산·충돌 해석
- 과거 유사 경로 또는 투명한 확률 모델 기반 5D / 20D 조건부 분포
- 시간순 walk-forward 검증, 겹치는 forward window 제거, 표본·기준 확률·검증 상태 공개
- 기존 Market Context 경제사이클의 hero, horizon, path, evidence, ribbon 패턴을 재사용한 Futures Macro React UI
- 현재 `과거 점검`을 핵심 `패턴 전망` 흐름으로 교체
- DB-backed runtime과 기존 futures daily OHLCV source boundary 유지
- desktop / mobile Browser QA와 회귀 테스트

### Out Of Scope

- 장기 경기 국면 예측 또는 경제사이클 대체
- 개별 선물 계약의 가격 목표
- 매수·매도·승인·선정·통과 표현
- Fed Funds / SOFR futures curve, CFTC positioning, options skew, 신규 유료 provider
- continuous futures roll 정규화 방식의 대규모 재설계
- Backtest, Practical Validation, Final Review, Portfolio Monitoring의 판단 로직 변경
- provider run / row / failure 수치를 주인공으로 만드는 진단 패널

## Tentative Stages

1. **설계 계약**
   - 목적: 시간축, 결과 대상, 검증·UI 경계를 고정한다.
   - 범위: 이 task 문서.
   - 완료 조건: 사용자 설계 검토와 승인.

2. **패턴 상태 V1**
   - 목적: 1D / 5D / 20D를 `충격 -> 지속 -> 체제`로 연결한다.
   - 범위: futures macro service와 focused tests.
   - 완료 조건: 현재 상태, persistence, transition, breadth, conflict payload가 point-in-time으로 생성된다.

3. **조건부 전망 / 검증 V1**
   - 목적: 현재 다중 기간 상태 이후 5D / 20D 결과를 기준 확률과 비교한다.
   - 범위: 별도 pattern validation service와 tests.
   - 완료 조건: walk-forward, purge / embargo, 독립 episode, minimum sample, unavailable gate가 검증된다.

4. **React Workbench V2**
   - 목적: Market Context와 같은 시각적 문법으로 현재·경로·전망·근거를 한 흐름에서 읽게 한다.
   - 범위: Futures Macro payload bridge와 React component / CSS.
   - 완료 조건: 사용자가 첫 화면에서 현재 체제, 5D / 20D 우위, 바뀌는 조건을 확인한다.

5. **실데이터 검증 / QA / 문서 정렬**
   - 목적: 실제 저장 표본에서 과도한 확률 표현과 반응형 회귀를 차단한다.
   - 범위: actual snapshot, desktop / mobile Browser QA, durable docs sync.
   - 완료 조건: 검증 결과와 스크린샷이 남고, 전체 roadmap 5/5 상태가 문서에 반영된다.

## Stop Condition

- 현행 5.4년 표본이 minimum sample / 독립 episode gate를 만족하지 못하면 확률을 억지로 공개하지 않는다.
- 이 경우 V1 UI는 현재 패턴과 `전망 검증 부족`을 표시하고, 데이터 history 확장을 별도 승인 범위로 남긴다.
- 신규 provider 또는 DB schema 변경이 필요해지면 현재 task를 확장하지 않고 사용자에게 별도 승인을 요청한다.
