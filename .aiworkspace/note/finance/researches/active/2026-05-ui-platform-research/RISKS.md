# Risks And Open Questions

## Key Risks

| Risk | Severity | Why it matters | Mitigation |
| --- | --- | --- | --- |
| API extraction expands too far | High | full refactor로 번지면 product work가 멈출 수 있다 | read-only contract 1개부터 시작 |
| Existing Streamlit behavior changes | High | session state와 registry write path가 복잡하다 | Streamlit UI를 먼저 유지하고 service call만 안쪽으로 교체 |
| Frontend pilot becomes a rewrite | High | Next.js pilot이 전체 UI migration으로 커질 수 있다 | Selected Dashboard read-only scope를 고정 |
| Schema mismatch with registries | Medium | JSONL registry가 append-only라 backward compatibility가 필요하다 | versioned read model을 만든다 |
| Chart library premature choice | Medium | TradingView/Plotly/ECharts/Recharts 선택이 data contract보다 앞서면 lock-in 발생 | chart-ready series contract부터 만든다 |
| FastAPI deployment complexity | Medium | local app에서 API server lifecycle과 CORS/dev server가 추가된다 | local-only/internal API로 시작하고 runbook 작성 |
| Auth/multi-user underestimation | Medium | 상용화 시 auth, permissions, audit log가 큰 과제가 된다 | pilot에서는 제외하고 later phase로 둔다 |
| Live trading scope creep | High | UI가 상용처럼 보이면 broker/order 요구가 따라올 수 있다 | Final Review / Selected Dashboard의 non-trading boundary를 계속 표시 |

## Open Questions

| Question | Needed before |
| --- | --- |
| Next.js pilot은 별도 app 디렉토리로 둘 것인가, monorepo package로 둘 것인가? | Phase C 시작 전 |
| API layer 위치는 `app/api`, `finance/api`, `app/web/api` 중 어디가 좋은가? | Phase A 시작 전 |
| Pydantic v2 사용 여부와 현재 dependency 상태는 어떤가? | Phase A 시작 전 |
| registry JSONL read model을 어디까지 versioning할 것인가? | Phase A 시작 전 |
| selected dashboard가 읽어야 하는 minimum artifact id set은 무엇인가? | Phase A/B 시작 전 |
| local dev server는 Streamlit과 FastAPI/Next.js를 어떻게 함께 띄울 것인가? | Phase B/C 시작 전 |

## Validation Gaps

- 실제 Next.js bundle / chart library 성능은 아직 테스트하지 않았다.
- FastAPI를 현재 venv dependency에 추가해도 충돌이 없는지 확인하지 않았다.
- Selected Portfolio Dashboard의 exact data contract는 코드 레벨로 아직 추출하지 않았다.
- Dash Enterprise는 공식 product page 기반 비교이며, 실제 비용/라이선스/운영 적합성은 별도 조사 필요하다.
- TradingView Advanced Charts는 licensing and private-use 조건 확인이 필요하다.

## Recommended Next Validation

1. `SelectedPortfolioSnapshot` read model을 Streamlit 없이 생성할 수 있는지 확인한다.
2. 해당 snapshot을 JSON fixture로 저장하고 Next.js mock page에서 읽는 spike를 한다.
3. FastAPI endpoint를 붙이기 전 service function test를 먼저 만든다.
4. pilot 후 Streamlit 화면과 Next.js 화면의 사용자 흐름 차이를 비교한다.
