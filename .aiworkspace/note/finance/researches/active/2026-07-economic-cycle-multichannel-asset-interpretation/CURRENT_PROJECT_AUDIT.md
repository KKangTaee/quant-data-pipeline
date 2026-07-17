# Current Project Audit

Status: Active
Last Updated: 2026-07-17

## Summary

현재 경제사이클 자산 카드는 네 canonical factor를 자산별 `FAVORABLE/BURDEN/MIXED`로 축약하고, 금·달러의 5/21/63거래일 가격 방향과 `ALIGNED/DIVERGENCE`로 비교한다. 읽기는 간단하지만 미국 경기 상태를 자산가격의 기준 방향처럼 보이게 하고, 실제 가격에 영향을 주는 중간 전달경로를 생략한다.

## Current Product Promise

Overview Market Context는 DB-backed evidence로 시장 맥락을 설명하는 read-only 사용자 화면이다. 투자 승인, 목표가격, 매매 신호, 원격 provider 직접 호출은 소유하지 않는다.

## Current Workflow

`경제사이클 factor evidence -> 자산별 orientation -> 지지/부담 판정 -> 금·달러 실제 가격 -> 같은/서로 다른 방향 -> React 카드` 순서다.

## Implemented Capabilities

- 미국 경제사이클: activity, labor/income, financial/leading, inflation/policy factor와 현재/+1M/+2M 확률
- 시장 맥락: 저장된 `VIXCLS`, `T10Y3M`, `BAA10Y`
- vintage/PIT 맥락: `BAMLH0A0HYM2`, `T10YIE`, `FEDFUNDS` 등
- 가격: `GC=F`, `DX-Y.NYB` 5/21/63거래일 수익률
- 자산 카드: 채권·금리, 주식, 금, 달러, 원자재의 조건부 설명

## Surface Role Classification

`Workspace > Overview > Market Context > 경제 사이클`은 사용자-facing research surface다. 데이터 수집·실행·진단 패널이 아니라 현재 판단과 근거를 읽는 화면이어야 한다.

## Strengths

- UI/provider 직접 호출 없이 DB -> loader -> service -> React 경계를 유지한다.
- 경제 기준일과 가격 기준일, 실제 symbol, 자료 부족 상태를 공개한다.
- 자산가격 예측과 경제사이클 publication gate를 분리한다.

## Weak Points

- macro factor가 자산 방향으로 바로 번역되어 금리·실질금리·달러·위험선호 같은 전달경로가 빠진다.
- `같은 방향/서로 다른 방향`은 단순 비교 상태인데 인과 설명처럼 읽힌다.
- 유리한 요인과 불리한 요인을 개수로 축약해 상반된 경로의 강도·신선도·커버리지를 충분히 보여주지 못한다.
- 현재 가격 움직임을 설명하지 못한 경우 `미측정 요인`과 `측정했지만 반대인 요인`을 구분하지 않는다.

## Data And Validation Risks

- 현재 `macro_series_observation`에는 VIX, 10년-3개월 금리차, Baa-10년 신용스프레드가 있으나 2년물·10년물 개별 금리와 10년 실질금리는 없다.
- economic-cycle vintage에는 기대인플레이션과 연방기금금리가 있지만 시장의 향후 정책금리 기대 자체는 없다.
- 동시 움직임은 인과관계 증명이 아니다. 문장은 `가격을 움직였다`가 아니라 `가격 방향과 함께 관측됐다`를 기본으로 해야 한다.
- 연속선물 가격에는 계약 교체 효과가 포함될 수 있다.

## UX / Workflow Friction

- 사용자는 `경제상태상 금이 올라야 하는데 하락했다`로 읽게 된다.
- 실제로 필요한 질문은 `어떤 전달경로가 서로 상충했고, 현재 측정 가능한 경로 중 무엇이 가격 방향과 가까웠는가`다.

## Documentation Or Handoff Drift

기존 문서는 `경제 배경/가격 일치·불일치`를 완료 계약으로 기록한다. 새 설계가 승인되면 이를 `경제 조건/전달경로/실제 가격/설명 범위`로 승격해야 한다.

## Benchmark Questions

- 측정된 경로와 미측정 경로를 한 카드에서 어떻게 구분할 것인가?
- 상관을 인과처럼 보이지 않게 하는 문장·badge·confidence 계약은 무엇인가?
- 금·달러 파일럿 계약을 채권 곡선과 원자재 하위군에 재사용할 수 있는가?

## Resolved Design Decisions

- 파일럿에는 `DGS2`, `DGS10`, `DFII10`을 신규 수집한다. `DGS2`는 관측된 단기 국채금리 경로이며 직접적인 정책금리 선물이나 인하 기대 데이터로 표현하지 않는다.
- 5거래일은 단기 맥락, 21·63거래일은 경로 방향에 사용한다. 최근 5년 동일 horizon 절대변화의 중앙값보다 작은 움직임은 중립 처리한다.
- 금·달러는 공통 다중 경로 계약으로 전환한다. 채권·주식·원자재는 단계적 확장 전까지 자산 방향 결론을 노출하지 않고 시장 경로 미연결 상태를 명시한다.
- 승인된 UI는 흰색 경로 카드, 왼쪽 컬러 강조선 없음, 그룹 배경색 없음이다.
