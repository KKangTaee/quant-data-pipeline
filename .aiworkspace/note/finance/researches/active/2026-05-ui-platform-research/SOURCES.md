# Sources

Access date: 2026-05-14

## Local Project Sources

| Label | Source | Used for |
| --- | --- | --- |
| LOCAL-PRODUCT | `.aiworkspace/note/finance/docs/PRODUCT_DIRECTION.md` | product purpose, evidence-first workflow, live trading boundary |
| LOCAL-ARCH | `.aiworkspace/note/finance/docs/architecture/README.md` | ingestion -> DB -> loader -> runtime -> Streamlit architecture |
| LOCAL-FLOW | `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md` | Backtest, Practical Validation, Final Review, Selected Portfolio Dashboard flow |
| LOCAL-CODE-STREAMLIT | `app/web/*.py` via `rg` | Streamlit import/session_state coupling |
| LOCAL-CODE-RUNTIME | `app/web/runtime/*.py` | possible service/API extraction boundary |

## Web Sources

| Label | Source | Publisher | Source type | Used claim | Confidence | Limitations |
| --- | --- | --- | --- | --- | --- | --- |
| WEB-STREAMLIT-STATE | https://docs.streamlit.io/develop/concepts/architecture/session-state | Streamlit | official docs | Streamlit reruns script top-to-bottom on interaction; session state persists across reruns | High | Does not itself say Streamlit is unsuitable for production |
| WEB-STREAMLIT-FLOW | https://docs.streamlit.io/develop/api-reference/execution-flow | Streamlit | official docs | default execution reruns app; forms/fragments/rerun/stop are control flow tools | High | Newer Streamlit features reduce some pain but do not create independent frontend architecture |
| WEB-STREAMLIT-COMPONENTS | https://docs.streamlit.io/develop/concepts/custom-components/overview | Streamlit | official docs | custom components can integrate web technology and support bidirectional communication | High | Component v2 is improving; product decision should be revisited after hands-on spike |
| WEB-FASTAPI | https://fastapi.tiangolo.com/ | FastAPI | official docs | FastAPI provides Python API framework, OpenAPI docs, deployment/test ecosystem | High | Framework choice still requires local spike |
| WEB-NEXTJS | https://nextjs.org/docs | Vercel/Next.js | official docs | Next.js provides routing, rendering, data fetching, API route capabilities | High | Next.js value for this project is UX/product architecture, not SEO |
| WEB-DASH-ENTERPRISE | https://plotly.com/dash/ | Plotly | official product page | Dash Enterprise targets production Python data apps with auth, embedding, job queues, data caching | Medium-High | Product marketing page; pricing/vendor lock-in requires separate evaluation |
| WEB-DASH-APP-MANAGER | https://plotly.com/dash/app-manager/ | Plotly | official product page | App Manager centralizes deployment, sharing, environment management | Medium-High | Enterprise product, not open-source Dash alone |
| WEB-DASH-JOB-QUEUE | https://plotly.com/dash/job-queue/ | Plotly | official product page | long-running tasks benefit from job queue semantics in production data apps | Medium-High | Marketing claim, but pattern aligns with current project needs |
| WEB-QUANTCONNECT-LEAN | https://www.quantconnect.com/docs/v2/writing-algorithms/key-concepts/algorithm-engine | QuantConnect | official docs | LEAN is an engine used for research/backtesting/live trading and powers the web platform | High | finance project should not inherit live trading scope |
| WEB-QUANTROCKET | https://www.quantrocket.com/docs/ | QuantRocket | official docs | JupyterLab primary UI, separate deployments for research/backtesting vs data/live; CLI/API backtests and tear sheets | High | Platform architecture differs from current project but patterns are relevant |
| WEB-OPENBB-DOCS | https://docs.openbb.co/ | OpenBB | official docs | ODP supports REST, Python, Jupyter, Excel and research dashboard applications | High | Product scope includes broader data platform |
| WEB-OPENBB-BACKEND | https://docs.openbb.co/workspace/developers/data-integration | OpenBB | official docs | Workspace custom backend is an API with widget definitions | High | OpenBB-specific integration model |
| WEB-OPENBB-API | https://docs.openbb.co/odp/python/extensions/interface/openbb-api | OpenBB | official docs | FastAPI/OpenAPI can be converted into Workspace backend/widget definitions | High | Useful as pattern, not necessarily target integration |
| WEB-TRADINGVIEW | https://www.tradingview.com/charting-library-docs/latest/introduction/ | TradingView | official docs | Advanced Charts is standalone client-side financial visualization requiring own data source; compatible with JS frameworks | High | Licensing/private use constraints must be checked before adoption |
| WEB-COMPOSER | https://www.composer.trade/ | Composer | official product page | AI strategy creation, visual strategy editor, backtest comparison, historical allocation, fees/slippage UI | Medium | Product includes brokerage/live execution, which is out of scope |

## Source Quality Notes

- Official docs were preferred over blogs or secondary reviews.
- Product marketing pages were used for feature pattern extraction, not for hard technical claims.
- Reddit and review sites were intentionally not used as primary evidence.
- For Streamlit, the conclusion is an inference from documented execution model plus local code coupling, not a claim made by Streamlit.

## 2026-05-19 Refocus Source Update

Access date: 2026-05-19

### Local Re-Audit Sources

| Label | Source | Used for |
| --- | --- | --- |
| LOCAL-2026-05-19-APPWEB-COUNT | `find app/web -name '*.py' \| wc -l` | `app/web` has 45 Python files |
| LOCAL-2026-05-19-STREAMLIT-IMPORTS | `rg -l "import streamlit\|from streamlit" app/web \| wc -l` | 18 `app/web` files import Streamlit |
| LOCAL-2026-05-19-SESSION-FILES | `rg -l "st\\.session_state" app/web \| wc -l` | 19 files use Streamlit session state |
| LOCAL-2026-05-19-SESSION-HITS | `rg -c "st\\.session_state" app/web` | major session state concentration in `backtest_common.py`, `backtest_single_forms.py`, `backtest_compare.py`, `streamlit_app.py` |
| LOCAL-2026-05-19-RUNTIME | `find app/web/runtime -maxdepth 1 -type f -name '*.py'`; `rg "import streamlit\|st\\." app/web/runtime` | runtime folder has 10 modules and no Streamlit import hit |
| LOCAL-2026-05-19-SERVICE-DIRS | `find app -maxdepth 2 -type d`; `find app/api app/services -name '*.py'` | `app/api` and `app/services` exist but have no Python service/API files yet |
| LOCAL-2026-05-19-TYPED-SCHEMA | `rg "BaseModel\|pydantic\|TypedDict\|@dataclass" app/web finance` | no typed request/response model layer found in inspected paths |
| LOCAL-2026-05-19-PYPROJECT | `pyproject.toml` | current declared dependency includes Streamlit but not FastAPI/Pydantic explicitly |
| LOCAL-2026-05-19-SINGLE-RUNNER | `app/web/backtest_single_runner.py` | strategy dispatch, Streamlit spinner/session state, history append are currently coupled |
| LOCAL-2026-05-19-PV-HELPERS | `app/web/backtest_practical_validation_helpers.py` | diagnostics, registry append, session handoff, and Streamlit import coexist |

### Web Source Refresh

| Label | Source | Publisher | Source type | Used claim | Confidence | Limitations |
| --- | --- | --- | --- | --- | --- | --- |
| WEB-2026-05-19-STREAMLIT-APP-MODEL | https://docs.streamlit.io/get-started/fundamentals/summary | Streamlit | official docs | Streamlit apps run top-to-bottom and rerun on widget interaction; session state persists between reruns | High | This supports the coupling diagnosis, not a claim that Streamlit is unsuitable |
| WEB-2026-05-19-STREAMLIT-SESSION | https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state | Streamlit | official docs | callbacks execute before the app reruns top-to-bottom; session state is tied to a user session/WebSocket caveats | High | Streamlit provides tools to manage state; local code size determines severity |
| WEB-2026-05-19-FASTAPI | https://fastapi.tiangolo.com/ | FastAPI | official docs | FastAPI is a Python API framework based on standard Python type hints and OpenAPI/JSON Schema standards | High | Dependency and app lifecycle still require local spike |
| WEB-2026-05-19-NEXT-DATA | https://nextjs.org/docs/app/getting-started/fetching-data | Next.js | official docs | Next.js supports server/client data fetching and streaming patterns | High | Relevant after service/API contract exists |
| WEB-2026-05-19-NEXT-ROUTING | https://nextjs.org/docs/pages/building-your-application/routing/linking-and-navigating | Next.js | official docs | Next.js routing supports URL-based navigation and links | High | Does not decide whether this project needs a frontend migration |
| WEB-2026-05-19-TRADINGVIEW | https://www.tradingview.com/charting-library-docs/latest/getting_started/Key-Features/ | TradingView | official docs | advanced charting is client-side and requires data supplied by the application | Medium-High | Licensing/access restrictions require separate adoption review |
