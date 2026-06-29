# Overview Market Context Events Data Trust V1 Plan

## 이걸 하는 이유?

Market Context 1차/2차로 시장 브리프와 갱신 반영 흐름은 좋아졌지만, CPI/FOMC 같은 핵심 macro event가 누락되면 사용자가 금리 압력이나 위험 선호를 잘못 해석할 수 있다.
이번 3차는 Market Context를 진단 패널로 키우지 않고, 시장 해석에 필요한 주요 이벤트와 자료 주의점만 믿고 읽을 수 있게 만드는 data trust 개선이다.

## 전체 흐름

- 1차 완료: Market Context를 guide/card 구조에서 시장 브리프 흐름으로 재배치했다.
- 2차 완료: 보조 갱신 후 상단 Market Context가 최신 snapshot을 다시 읽도록 cache/rerun UX를 보정했다.
- 3차 현재: CPI/PPI/Employment/GDP/FOMC coverage, BLS HTML/ICS fallback, recent+upcoming 이벤트 read model, Data Health 노출 범위를 보강한다.
- 4차 후속: 과거 유사국면 / 향후 예측 기능, 섹터 ETF 장기 데이터 coverage, Consumer Defensive/XLP 파일럿 가능성을 별도 검토한다.

## 3차 Scope

- Overview Events와 Market Context에서 CPI/PPI/Employment/GDP/FOMC를 주요 macro event로 우선 표시한다.
- Events read model은 가까운 미래만 보지 않고 최근 7일과 향후 14일을 함께 본다.
- BLS HTML parser와 BLS `.ics` fallback parser가 CPI/PPI/Employment 일정을 파싱/저장 가능한지 fixture 기반 테스트로 검증한다.
- Market Context 안의 이벤트는 "최근 확인 필요"와 "다가오는 변수" 수준의 간결한 해석 변수로 둔다.
- Data Health는 Market Context에서 큰 진단 패널이 아니라 자료 주의점으로만 남기고, 상세 수집 상태는 Data Health 탭/접힘 영역에 둔다.

## Out Of Scope

- 과거 유사국면 / 향후 예측 기능 구현.
- 새 provider 추가.
- DB schema 변경.
- registry/saved JSONL rewrite.
- run_history/generated artifact stage.
- Backtest, Practical Validation, Final Review, Operations 수정.
- Market Context를 guide tab으로 되돌리거나 Data Health를 첫 화면 중심 UI로 키우는 작업.

## TDD Plan

1. 현재 DB와 read model 기준 event coverage를 먼저 측정해 `NOTES.md`에 남긴다.
2. `tests/test_service_contracts.py`에 failing tests를 추가한다.
   - 주요 macro event가 earnings보다 우선하며 recent+upcoming window를 함께 반환한다.
   - macro week lane이 최근 주요 이벤트와 다가오는 주요 이벤트를 분리한다.
   - Market Context cue가 CPI/FOMC 같은 이벤트를 간결한 해석 변수로 노출한다.
   - BLS HTML/ICS fixture가 CPI/PPI/Employment를 모두 파싱한다.
   - Data Health 관련 Market Context copy가 상세 job/row 진단으로 전면화되지 않는다.
3. failing tests를 확인한 뒤 최소 구현으로 green을 만든다.
4. requested compile, focused pytest, Streamlit Browser QA, screenshot, commit을 완료한다.

## Completion Conditions

- CPI/PPI/Employment/GDP/FOMC coverage 현재 상태를 명확히 기록한다.
- CPI 같은 중요 macro event가 Events/Market Context에서 누락되거나 earnings에 묻히는 문제가 완화된다.
- recent + upcoming 주요 이벤트 흐름이 read model/UI에 반영된다.
- Market Context Data Health 노출은 사용자 판단에 필요한 최소 문구로 제한된다.
- py_compile, focused tests, Browser QA를 수행하고 결과를 기록한다.
