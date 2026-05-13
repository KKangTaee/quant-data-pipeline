# Benchmarks

## Benchmark Matrix

| Benchmark | What it is | Relevant pattern | Implication for finance project |
| --- | --- | --- | --- |
| Streamlit | Python-first app framework | top-to-bottom rerun, session state, custom components | internal research/ops console에는 계속 적합. product-grade multi-stage app은 state/API 분리가 필요 |
| FastAPI | Python API framework | typed request/response, OpenAPI docs, async support | Python quant engine 앞에 thin service contract를 만들기 좋다 |
| Next.js / React | JS/TS frontend framework | routing, rendering options, component ecosystem | selected dashboard, review viewer, chart-heavy UI에 적합 |
| Plotly Dash Enterprise | production Python data app platform | auth, app manager, job queue, embedding, data caching | Python-only productization 대안이지만 license/platform dependency가 생긴다 |
| QuantConnect / LEAN | quant engine + web platform | engine과 web platform 분리, local/cloud execution | engine boundary와 run artifact 중심 UX가 중요하다 |
| QuantRocket | Docker/Jupyter/CLI/API quant platform | Jupyter research UI, CLI/API backtests, tear sheets, separate deployments | research와 production/ops deployment를 분리하는 패턴이 유용하다 |
| OpenBB Workspace / ODP | financial data platform + workspace widgets | custom backend API, widgets.json, FastAPI conversion | API를 만들어 workspace/widget frontend에 연결하는 방향과 닮아 있다 |
| TradingView Advanced Charts | financial charting JS library | client-side financial chart, custom data source, React compatibility | 상용 감각의 chart UX는 JS frontend에서 훨씬 자연스럽다 |
| Composer | no-code/AI strategy builder and brokerage | AI strategy creation, visual editor, backtest comparison, historical allocation | 사용자가 이해하기 쉬운 strategy editor와 allocation history 표현이 강하다 |

## Streamlit

Streamlit 공식 문서는 사용자가 widget과 상호작용할 때 script가 top-to-bottom으로 rerun되고, session state가 rerun 사이의 값을 유지한다고 설명한다. 이 모델은 빠른 Python app에는 좋지만, 현재 finance처럼 여러 단계의 product state가 많은 workflow에서는 state key와 rerun side effect가 늘어난다.

Streamlit custom components는 web technology나 React/TypeScript component를 붙일 수 있는 통로를 제공한다. 하지만 custom component는 Streamlit 안에서 복잡한 frontend를 보강하는 수단이지, typed API와 독립 frontend app을 대체하는 architecture boundary는 아니다.

Takeaway:

- Streamlit 유지 가치는 높다.
- 단, custom component로 모든 문제를 해결하려 하기보다 API boundary를 먼저 만드는 편이 낫다.

## FastAPI

FastAPI는 Python service layer를 만들기에 가장 직접적인 후보로 보인다. 현재 finance core가 Python이고 runtime adapter도 Python이므로, FastAPI를 얇게 얹으면 quant engine을 다시 쓰지 않고도 typed endpoint, OpenAPI, test client, async job wrapper를 만들 수 있다.

Takeaway:

- `app/api` 또는 `finance/api` 후보를 만들어 runtime contract를 먼저 안정화한다.
- 처음부터 public API를 만들기보다 local/internal API로 시작한다.

## Next.js / React

Next.js는 routing, rendering, API integration, React component ecosystem을 제공한다. finance 프로젝트에서 Next.js가 필요한 이유는 SEO가 아니라 product UX다. 특히 review link, dashboard URL state, chart/table interaction, responsive layout, keyboard/hover/tooltip, component reuse가 필요할 때 가치가 커진다.

Takeaway:

- 첫 Next.js pilot은 write-heavy workflow보다 read-only review/dashboard가 적합하다.
- Selected Portfolio Dashboard 또는 Final Review evidence viewer가 후보로 좋다.

## Plotly Dash Enterprise

Dash Enterprise는 Python data app의 production 운영 문제를 직접 겨냥한다. 공식 제품 페이지는 app manager, authentication, embedding, job queue, data caching을 강조한다. 이는 현재 finance 프로젝트가 Streamlit에서 부딪힐 가능성이 높은 운영 문제와 거의 같다.

Takeaway:

- Python-only path를 유지하고 싶다면 Dash Enterprise/Dash 계열은 비교 가치가 있다.
- 다만 open-source Dash만으로는 product-grade 운영 기능이 자동 해결되지 않고, Enterprise는 벤더/비용 의존이 생긴다.

## QuantConnect / LEAN

QuantConnect는 LEAN engine을 web platform의 핵심으로 사용한다. 공식 문서는 LEAN이 research, backtesting, live trading에 쓰이는 engine이고, QuantConnect web platform을 구동한다고 설명한다. finance 프로젝트는 live trading을 목표로 하지 않지만, engine과 web platform의 분리 패턴은 참고할 만하다.

Takeaway:

- Python quant engine은 UI와 분리된 reusable service로 다뤄야 한다.
- run artifact, dataset, broker/live boundary를 명확히 나누는 태도가 중요하다.

## QuantRocket

QuantRocket 공식 문서는 JupyterLab을 주요 UI로 두고, team 환경에서는 data/live deployment와 research/backtesting deployment를 나누는 전략을 설명한다. 또한 CLI, notebook, HTTP API로 backtest를 실행하고 tear sheet를 만든다.

Takeaway:

- research UI와 ops/product UI를 하나로 합치지 않는 것이 자연스럽다.
- finance 프로젝트도 Streamlit internal console과 product frontend를 분리할 수 있다.

## OpenBB Workspace / ODP

OpenBB Workspace는 custom backend API를 통해 외부 data source를 widget으로 연결한다. OpenBB ODP 문서는 FastAPI instance나 OpenAPI JSON을 Workspace backend/widget 정의로 변환하는 tooling을 제공한다.

Takeaway:

- "Python API + frontend workspace/widget" 패턴은 이미 금융 데이터 제품에서 쓰이는 방향이다.
- finance 프로젝트도 먼저 API/schema를 만들면 이후 자체 Next.js뿐 아니라 외부 workspace 연동 가능성이 생긴다.

## TradingView Advanced Charts

TradingView Advanced Charts는 standalone client-side financial visualization solution이며, 데이터는 자체 API로 공급해야 한다. 문서는 charting solution이 JavaScript/HTML/CSS 기반이고 React/Angular/Vue와 호환된다고 설명한다.

Takeaway:

- 고급 차트 UX를 원하면 JS frontend를 피하기 어렵다.
- finance 프로젝트의 DB/loader 결과를 chart datafeed contract로 변환하는 feature가 필요해질 수 있다.

## Composer

Composer는 자연어/AI strategy creation, no-code visual editor, backtest comparison, historical allocation graph, fees/slippage display를 전면에 둔다. live brokerage execution은 finance 프로젝트 scope 밖이지만, strategy understanding UX는 참고 가치가 크다.

Takeaway:

- 사용자는 전략 코드를 직접 보지 않아도 전략 조건, weighting, 조건문, filter, 성과 비교를 이해할 수 있어야 한다.
- finance 프로젝트의 강점인 Practical Validation과 Final Review를 더 시각적이고 설명 가능한 화면으로 만들 여지가 있다.

## Benchmark Conclusion

유사 제품과 프레임워크의 공통 패턴은 다음과 같다.

| Pattern | Meaning |
| --- | --- |
| Engine is not the UI | quant/backtest engine은 재사용 가능한 service나 CLI/API로 유지한다 |
| Research UI and product UI split | notebook/Streamlit 같은 빠른 연구 화면과 polished product 화면은 역할이 다르다 |
| Run artifacts matter | backtest 결과, validation evidence, decision record가 재실행/공유 가능한 artifact여야 한다 |
| Long-running work needs queue semantics | backtest, ingestion, validation은 request/response callback이 아니라 job으로 다뤄야 한다 |
| Financial charts are frontend-heavy | 상용 수준 chart/table UX는 JS component ecosystem이 강하다 |
| Live trading boundary must stay explicit | 제품화 UI가 생겨도 broker order / auto rebalance와 research decision은 분리해야 한다 |
