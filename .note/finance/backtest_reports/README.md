# Backtest Reports

## 목적

이 폴더는 **백테스트 결과를 설명하는 Markdown 문서만 따로 모아두는 공간**이다.

쉽게 말하면:

- phase 문서: 왜 이 작업을 했는지, 어떤 순서로 진행했는지
- backtest report 문서: 어떤 전략을 어떤 설정으로 돌렸고, 결과가 어땠는지

를 분리해서 관리하기 위한 폴더다.

## 이 폴더에 넣는 문서

다음 성격의 문서는 앞으로 이 폴더에 두는 것을 기본으로 한다.

- 특정 전략 후보 탐색 결과
- 조건부 포트폴리오 탐색 결과
- `SPY` 비교 결과
- `CAGR / MDD / promotion` 목표를 기준으로 한 검색 결과
- 사용자가 다시 재현해볼 수 있는 backtest 가이드 문서

즉, 문서의 중심이

- “무엇을 구현했는가”가 아니라
- “어떤 백테스트를 돌렸고 결과가 무엇인가”

라면 이 폴더에 두는 것이 맞다.

## 이 폴더에 넣지 않는 문서

다음 문서는 계속 기존 위치를 유지한다.

- phase 계획 문서
- phase TODO 보드
- phase 체크리스트
- architecture / policy / contract 문서
- package 전체 종합 문서

즉, **실행 관리 문서**는 phase 폴더에 두고, **결과 리포트 문서**는 이 폴더에 둔다.

## 권장 운영 방식

1. phase 작업 중 백테스트를 많이 돌린다
2. 결과가 durable하면 이 폴더에 report 문서를 만든다
3. 전략별 허브 문서를 만든다
4. 동시에 해당 전략의 `*_BACKTEST_LOG.md`에 run 기록을 append 한다
5. phase 문서에는 그 report를 링크만 남긴다

이렇게 하면:

- phase 문서는 작업 흐름을 보기 좋고
- backtest report 폴더는 전략 기준으로 결과 검색이 쉬워진다
- 전략별 log 문서를 보면
  - 어떤 세팅으로 돌렸는지
  - 결과가 어땠는지
  - 다음에 무엇을 다시 봐야 하는지
  를 빠르게 추적할 수 있다

## 전략별 backtest log 운영 원칙

앞으로는 전략별 허브만 두는 것이 아니라,
각 전략마다 `*_BACKTEST_LOG.md`를 같이 유지하는 것을 기본으로 한다.

기본 목적은 이거다.

- “어떤 전략을 어떤 설정으로 돌렸는가”
- “결과가 어땠는가”
- “왜 의미가 있었는가”

를 전략 단위로 누적 관리하는 것

권장 규칙:

1. 의미 있는 backtest를 하나 완료하면 해당 전략 log에 append 한다
2. 기록은 지우지 않고 누적한다
3. 최소한 아래 항목은 남긴다
   - 목표
   - 기간 / universe
   - 핵심 설정
   - factor 또는 ticker
   - CAGR / MDD / Promotion / Shortlist / Deployment
   - 해석과 다음 액션
4. 공통 형식은 `strategies/BACKTEST_LOG_TEMPLATE.md`를 기준으로 맞춘다

## 파일명 권장 규칙

권장 형식:

- `YYYY-MM-DD_<strategy-family>_<goal>.md`
- 또는
- `<strategy-family>_<goal>_BACKTEST_GUIDE.md`

예시:

- `2026-04-06_value_strict_spy_search.md`
- `2026-04-06_quality_value_low_drawdown_search.md`
- `VALUE_RAW_WINNER_BACKTEST_GUIDE.md`

파일명은 다음 중 하나가 바로 보이도록 짓는 것이 좋다.

- 전략 family
- 탐색 목표
- 비교 기준
- 결과 성격

## 현재 원칙

현재는 새로 만드는 결과 중심 문서는 이 폴더에 두는 것을 기본으로 하고, 많이 참조되는 기존 결과 문서도 점진적으로 이 폴더로 옮긴다.

Phase 13 결과 문서는 이미 `.note/finance/backtest_reports/phase13/`로 정리했고, 기존 phase 경로에는 호환용 안내 stub를 남겨두었다.
Phase 14 결과 문서는 `.note/finance/backtest_reports/phase14/`에 두고,
Phase 15 candidate-quality-improvement 결과는 `.note/finance/backtest_reports/phase15/`에 모은다.
현재 Phase 15에는

- `Value` downside-improvement
- `Value` factor-addition
- `Quality` controlled addition review
- `Quality + Value` controlled addition review

가 누적되고 있다.

또한 실제로 다시 찾아볼 때는:

- `strategies/` 아래 허브 문서부터 보고
- 필요할 때만 `phase13/` raw report archive를 여는 구조를 기본으로 한다.
