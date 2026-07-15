# Sources

Access date: 2026-07-16

Evidence labels:

- `Observed`: official UI/docs directly show the pattern.
- `Documented`: official docs or repository describe the pattern.
- `Claimed`: product page or marketing copy claims the pattern.
- `Inferred`: synthesis from multiple supported facts.
- `Unknown`: evidence is missing or unclear.

## Local Sources

| Source | Evidence | Notes |
| --- | --- | --- |
| `.aiworkspace/note/finance/docs/PRODUCT_DIRECTION.md` | Documented | Evidence-first, DB-backed, no-live-trading product boundary. |
| `.aiworkspace/note/finance/docs/ROADMAP.md` | Documented | Final Review eligible Gate와 evidence closure 방향. |
| `.aiworkspace/note/finance/docs/PROJECT_MAP.md` | Documented | Final Review와 Overview 소유 파일 경계. |
| `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md` | Documented | Backtest -> Practical Validation -> Final Review -> Monitoring 사용자 흐름. |
| `app/services/backtest_evidence_read_model.py` | Observed | 현재 strength/weakness, score, Level2 disposition, decision route 계약. |
| `app/web/backtest_final_review/page.py` | Observed | Streamlit Decision Desk, React orchestration, fallback, decision intent. |
| `app/web/components/final_review_investment_report/frontend/src/FinalReviewInvestmentReport.tsx` | Observed | 현재 report section 순서와 반복 노출. |
| `app/web/overview/market_context.py` | Observed | Market Context의 compact Streamlit heading. |
| `app/web/overview/market_context_helpers.py` | Observed | DB-backed React-first Market Context surface와 compact fallback. |
| Local Streamlit runtime `http://127.0.0.1:8505` | Observed | 2026-07-16 current Final Review와 Market Context 실제 화면 비교. |
| `.aiworkspace/note/finance/researches/active/2026-05-investable-workflow-gap-analysis/` | Documented | 이전 evidence packet/gate hardening 방향과 현재 과다 노출의 배경. |

## Web Sources

| Source | Evidence | Notes |
| --- | --- | --- |
| External web benchmark not required for approved scope | Unknown | 내부 기준 화면과 current runtime/code evidence로 1차 방향을 결정했다. 외부 pattern 비교는 후속 polish가 필요할 때만 수행한다. |

## Source Notes

- Prefer current, official, primary sources.
- Treat product marketing pages as feature-pattern evidence, not verified technical capability.
- Visual Companion mockup은 설계 대화 보조 자료이며 source-of-truth는 `RECOMMENDATION.md`다.
