# Current Project Audit

## Snapshot

finance 프로젝트는 Python 기반 quant research workspace로 발전해 있다. 현재 문서 기준 제품 방향은 `Backtest Analysis -> Practical Validation -> Final Review -> Selected Portfolio Dashboard`로 이어지는 evidence-first workflow다. 데이터는 provider에서 직접 UI로 가지 않고 `Ingestion -> DB -> Loader -> runtime -> UI` 흐름을 유지해야 한다.

현재 웹 구현은 Streamlit 중심이다. `app/web`에는 Python 파일 45개가 있고, 그중 18개가 `streamlit`을 직접 import한다. `st.session_state`는 19개 파일에 분포하며 `rg -c` 기준 1,148개 line hit가 있다. 이 숫자는 현재 UI가 단순 dashboard가 아니라 multi-stage workflow state machine 역할까지 Streamlit session state로 수행하고 있음을 보여준다.

## Current Capabilities

| Area | 현재 상태 |
| --- | --- |
| Data pipeline | provider ingestion, DB persistence, loader boundary가 durable docs에 정의되어 있다 |
| Backtest runtime | `app/web/runtime/backtest.py` 등 runtime adapter가 존재하고, UI와 완전히 같지는 않지만 분리 가능한 경계가 있다 |
| Backtest UX | Single Strategy, Compare, Candidate Review, Portfolio Proposal, Practical Validation, Final Review 흐름이 Streamlit page/panel로 구현되어 있다 |
| Evidence workflow | Practical Validation diagnostics, Final Review decision, Selected Portfolio Dashboard monitoring signal이 있다 |
| Registry / saved setup | append-only JSONL registry와 saved reusable portfolio setup 경계가 문서화되어 있다 |
| Product boundary | live approval, broker order, auto rebalance는 명시적으로 제외되어 있다 |

## Strengths

| Strength | Why it matters |
| --- | --- |
| Python-first research speed | 전략, factor, loader, validation을 같은 언어와 pandas ecosystem 안에서 빠르게 수정할 수 있다 |
| DB-backed runtime principle | UI가 provider/FRED를 직접 fetch하지 않는 원칙이 있어 API 분리의 기초가 이미 있다 |
| Workflow maturity | 단순 chart app이 아니라 후보 생성, 검증, 최종 판단, 선정 이후 모니터링까지 이어진다 |
| Evidence-first positioning | Composer류의 간단한 strategy builder보다 검증 근거와 practical validation에 강점이 있다 |
| Runtime/helper split | 일부 로직이 `app/web/runtime/*`, `*_helpers.py`로 빠져 있어 migration 후보를 고르기 쉽다 |

## Weaknesses

| Weakness | Evidence | Impact |
| --- | --- | --- |
| Streamlit coupling is broad | `app/web` 45개 Python 파일 중 18개가 `streamlit`을 직접 import | 프론트엔드 교체, API 재사용, headless test가 어렵다 |
| Session state is product state | 19개 파일에서 `st.session_state` 사용, `backtest_common.py`, `backtest_compare.py`, `backtest_single_forms.py`에 집중 | URL/deep-link, multi-user state, deterministic replay가 약하다 |
| Multi-stage workflow is hidden in UI state | active panel, requested panel, prefill payload, notice가 Streamlit session state로 연결된다 | API client, external frontend, automated workflow가 같은 흐름을 쓰기 어렵다 |
| Long-running job UX is limited | ingestion/backtest/revalidation은 Python callback과 Streamlit rerun 모델에 묶인다 | queue, progress, retry, cancellation, background notification을 제품화하기 어렵다 |
| Product polish ceiling | Streamlit widget/layout 중심 UI는 고급 chart interaction, mobile responsiveness, keyboard interaction, dense table editing에 한계가 있다 | 상용 UI로 보일 때 체감 품질이 낮아질 수 있다 |
| Auth / permission / collaboration boundary absent | 현재 docs는 local/internal workflow 중심이다 | 외부 사용자, 팀 단위 권한, shared review workflow로 확장하기 전 별도 설계가 필요하다 |
| Legacy path drift exists | `app/web/streamlit_app.py`는 glossary path를 `.note/finance/docs/GLOSSARY.md`로 읽으려 하지만 화면 copy는 `.aiworkspace/...`를 말한다 | 문서 구조 migration 이후 UI와 durable docs가 완전히 동기화되지 않은 신호다 |

## Streamlit Fit Assessment

Streamlit이 잘 맞는 영역:

- 내부 research console
- 빠른 strategy prototype
- ingestion / DB 상태 점검
- 단일 사용자 중심 backtest 실험
- admin/ops review page
- Python developer가 바로 수정하는 화면

Streamlit이 점점 부담이 되는 영역:

- 외부 사용자에게 보여줄 polished product UI
- 깊은 URL state와 shareable review link
- 여러 사용자가 같은 candidate/review를 협업하는 flow
- 차트 위 annotation, cross-filter, 고급 table editing
- background job queue, progress, cancellation
- typed API contract를 통한 다른 client 재사용

## Architecture Readiness

현재 구조는 full rewrite보다 staged extraction에 적합하다.

| Layer | Readiness | Comment |
| --- | --- | --- |
| Quant engine | 높음 | `finance/*` core는 Python에 유지해야 한다 |
| Runtime adapters | 중간 | `app/web/runtime/*`가 API service 후보지만, Streamlit assumptions를 더 걷어내야 한다 |
| Registry contracts | 중간 | JSONL registry는 읽고 쓰기 쉽지만 schema/version contract가 필요하다 |
| UI state | 낮음 | session state key가 많아 API request/response model로 정리해야 한다 |
| Frontend components | 낮음 | React/Next.js component system은 아직 없다 |

## Diagnosis

Streamlit은 현재까지 좋은 선택이었다. 빠른 개발과 Python 중심 검증에는 맞았다. 다만 지금의 제품은 단순 dashboard를 넘어 workflow product가 되었고, 다음 단계의 병목은 전략 엔진보다 UI state, job orchestration, product-grade interaction에 있다.

따라서 결론은 "Streamlit을 버린다"가 아니라 "Streamlit을 내부 console로 남기고, 외부/상용화 후보 화면은 API + React/Next.js로 점진 분리한다"가 더 안전하다.
