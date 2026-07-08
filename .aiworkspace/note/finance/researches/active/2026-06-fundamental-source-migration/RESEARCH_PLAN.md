# Fundamental Source Migration Research Plan

## 왜 이걸 하는가?

Market Movers와 backtest 화면이 재무제표 지표를 보여주기 시작하면서, `yfinance` broad fundamentals와 EDGAR statement ledger가 동시에 노출되고 있다. 사용자는 앞으로 yfinance 기반 재무제표 수집을 줄이고 EDGAR 기반 공식 원천으로 정리하려고 한다. UI를 더 다듬기 전에 데이터 원천, 백테스트 의존성, 최신 표시 기준을 먼저 확정해야 한다.

## 핵심 질문

1. yfinance 기반 financial statement collection을 없애도 되는가?
2. `edgartools` / EDGAR path를 신뢰할 수 있는가?
3. yfinance fundamentals에 의존한 backtest, loader, UI 기능을 EDGAR로 마이그레이션할 수 있는가?
4. 실사용 프로그램 관점에서 최선의 canonical source 전략은 무엇인가?
5. 수집, 백테스트, UX 최신 표시에는 각각 어떤 read model을 써야 하는가?
6. EDGAR 외 대안은 무엇이고, 어느 위치에 쓰는 것이 적절한가?

## 산출물

- `CURRENT_PROJECT_AUDIT.md`: 현재 코드 / DB / 기능 의존성 audit
- `BENCHMARKS.md`: 외부 source와 유사 접근 방식 비교
- `UI_PATTERNS.md`: compact UI에서 source/freshness를 노출하는 기준
- `RECOMMENDATION.md`: 권장 source architecture와 단계별 migration plan
- `RISKS.md`: 남은 data-quality / migration risk
- `SOURCES.md`: 확인한 공식/외부 source

## 이번 research의 경계

- 코드 변경 없음.
- DB schema 변경 없음.
- provider 추가 없음.
- yfinance 삭제 없음.
- UI fetch 추가 없음.
- 투자 신호, validation gate, Final Review decision 생성 없음.
