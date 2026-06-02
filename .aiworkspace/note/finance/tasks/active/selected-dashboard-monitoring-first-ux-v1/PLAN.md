# Selected Dashboard Monitoring First UX V1

## 이걸 하는 이유?

Selected Portfolio Dashboard는 매일 확인하는 운영 화면이어야 한다.
현재 화면은 portfolio setup과 strategy board가 먼저 보여서 이미 scenario를 설정한 portfolio도 매번 아래로 내려가야 한다.
상단에서 active portfolio의 monitoring scenario 상태를 바로 확인하고, 구성 수정은 아래 관리 영역에서 이어가게 한다.

## Scope

- `app/web/final_selected_portfolio_dashboard.py`
- Selected Dashboard visible section order
- Active portfolio monitoring empty / not configured states
- Portfolio scenario update action placement
- Durable flow docs and root handoff logs

## Out Of Scope

- Broker order, account sync, live approval, auto rebalance
- New background job or persisted monitoring result storage
- Final Review selected row mutation
- Saved portfolio JSONL rewrite or cleanup
- Strategy runtime / DB schema changes

## Acceptance

- Page entry shows Active Portfolio Monitoring Scenario before portfolio cards and strategy setup.
- No portfolio / no strategy / configured-not-run / normal run states are distinct and not shown as hard failures.
- Portfolio card shelf remains the active portfolio selector below the monitoring hero.
- Strategy board and `포트폴리오 시나리오 업데이트` are below the shelf.
- Detailed readiness / provider / freshness / open issue evidence stays below setup as detail.
- Saved setup and runtime contracts remain unchanged.
