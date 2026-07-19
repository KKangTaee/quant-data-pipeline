# Overview Sentiment CNN Component Status Badges Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make each CNN component rating immediately scannable with a compact server-tone-driven badge while preserving the existing evidence layout and AAII rendering.

**Architecture:** The sentiment service remains the sole owner of CNN thresholds and already publishes `rating` and `tone` on each `evidence.cnn_components` item. React adds a `data-tone` styling hook with a neutral fallback, and CSS maps the four existing tones to the approved berry, amber, slate, and teal badge treatments without changing score styling or row backgrounds.

**Tech Stack:** Python `unittest` source-contract tests, React/TypeScript, CSS, Vite production build, Streamlit Browser QA.

## Global Constraints

- Do not recompute CNN score thresholds in React.
- Use existing service tones exactly: `danger`, `warning`, `neutral`, `positive`.
- Keep the numeric score in the existing neutral foreground color.
- Keep the full rating text visible so color is never the only state signal.
- Missing or unknown tone uses `neutral`; missing rating text renders `-`.
- Apply the treatment only to CNN component evidence; AAII remains unchanged.
- Do not change DB, ingestion, loader, refresh action, payload version, Hero, current evidence cards, charts, outlook cards, or raw evidence tables.

## File Structure

- `tests/test_service_contracts.py`: owns the source-contract regression for the CNN tone badge and all four CSS tone variants.
- `app/web/streamlit_components/sentiment_workbench/src/SentimentEvidenceDisclosure.tsx`: renders the existing CNN rating as a badge and exposes the service tone through `data-tone`.
- `app/web/streamlit_components/sentiment_workbench/src/style.css`: owns compact badge dimensions, fallback styling, and the four approved tone palettes.
- `app/web/streamlit_components/sentiment_workbench/component_static/`: generated Vite production bundle committed with the source change.
- `.aiworkspace/note/finance/tasks/active/overview-sentiment-cnn-aaii-v1-20260719/{STATUS,NOTES,RUNS}.md`: records the approved visual contract and verified results.

---

### Task 1: Implement Server-Tone CNN Rating Badges

**Files:**
- Modify: `tests/test_service_contracts.py:8929`
- Modify: `app/web/streamlit_components/sentiment_workbench/src/SentimentEvidenceDisclosure.tsx:51-57`
- Modify: `app/web/streamlit_components/sentiment_workbench/src/style.css:818-843`
- Regenerate: `app/web/streamlit_components/sentiment_workbench/component_static/`

**Interfaces:**
- Consumes: existing `CnnEvidence.rating?: string` and `CnnEvidence.tone?: string` from `SentimentWorkbenchPayload.evidence.cnn_components`.
- Produces: `.sentiment-workbench__cnn-status-badge` with `data-tone="danger|warning|neutral|positive"`; unknown values fall back to `neutral`.

- [ ] **Step 1: Write the failing source-contract regression**

Add this method to `OverviewAutomationContractTests` in `tests/test_service_contracts.py`:

```python
def test_sentiment_react_cnn_component_ratings_use_tone_badges(self) -> None:
    source_root = Path("app/web/streamlit_components/sentiment_workbench/src")
    disclosure_source = (source_root / "SentimentEvidenceDisclosure.tsx").read_text(encoding="utf-8")
    react_style = (source_root / "style.css").read_text(encoding="utf-8")

    self.assertIn('className="sentiment-workbench__cnn-status-badge"', disclosure_source)
    self.assertIn('data-tone={item.tone || "neutral"}', disclosure_source)
    self.assertIn('{item.rating || "-"}', disclosure_source)
    for tone in ("danger", "warning", "neutral", "positive"):
        self.assertIn(
            f'.sentiment-workbench__cnn-status-badge[data-tone="{tone}"]',
            react_style,
        )
```

- [ ] **Step 2: Run the regression and verify RED**

Run:

```bash
.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_sentiment_react_cnn_component_ratings_use_tone_badges
```

Expected: one failure because the badge class and tone selectors do not exist.

- [ ] **Step 3: Render the existing rating as a tone-driven badge**

Replace the second metric `<div>` in `SentimentEvidenceDisclosure.tsx` with:

```tsx
<div>
  <b>{displayValue(item.score)}</b>
  <span
    className="sentiment-workbench__cnn-status-badge"
    data-tone={item.tone || "neutral"}
  >
    {item.rating || "-"}
  </span>
</div>
```

Do not add score thresholds, label parsing, or AAII classes.

- [ ] **Step 4: Add the approved compact badge palette**

Update the metric container and add these rules after the existing CNN row typography rules in `style.css`:

```css
.sentiment-workbench__cnn-evidence-row > div:nth-child(2) {
  justify-items: end;
  text-align: right;
}

.sentiment-workbench__cnn-status-badge {
  background: #f1f4f6;
  border: 1px solid #d5dde3;
  border-radius: 999px;
  color: #526176;
  display: inline-flex;
  font-size: 0.62rem;
  font-weight: 850;
  line-height: 1.2;
  max-width: 100%;
  padding: 3px 6px;
  text-align: center;
  white-space: normal;
}

.sentiment-workbench__cnn-status-badge[data-tone="danger"] {
  background: #fff0f3;
  border-color: #e8b9c3;
  color: #993d54;
}

.sentiment-workbench__cnn-status-badge[data-tone="warning"] {
  background: #fff2e5;
  border-color: #efd1ad;
  color: #9a5b2d;
}

.sentiment-workbench__cnn-status-badge[data-tone="neutral"] {
  background: #f1f4f6;
  border-color: #d5dde3;
  color: #526176;
}

.sentiment-workbench__cnn-status-badge[data-tone="positive"] {
  background: #e9f7f3;
  border-color: #b9dfd5;
  color: #0f766e;
}
```

- [ ] **Step 5: Run the focused regression and verify GREEN**

Run:

```bash
.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_sentiment_react_cnn_component_ratings_use_tone_badges
```

Expected: `Ran 1 test` and `OK`.

- [ ] **Step 6: Rebuild the production component**

Run:

```bash
cd app/web/streamlit_components/sentiment_workbench
npm run build
```

Expected: Vite completes successfully and writes hashed CSS/JS assets under `component_static/assets/`.

- [ ] **Step 7: Commit the implementation unit**

Stage only the test, React source, CSS, `component_static/index.html`, deleted old hashed assets, and newly generated hashed assets. Do not stage `.superpowers/` or QA PNG files.

```bash
git commit -m "Overview 심리 CNN 상태 배지 구현"
```

---

### Task 2: Verify Responsive UI And Synchronize Task Records

**Files:**
- Modify: `.aiworkspace/note/finance/tasks/active/overview-sentiment-cnn-aaii-v1-20260719/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-sentiment-cnn-aaii-v1-20260719/NOTES.md`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-sentiment-cnn-aaii-v1-20260719/RUNS.md`
- Generate but do not commit: `overview-sentiment-cnn-status-badges-qa.png`

**Interfaces:**
- Consumes: the Task 1 badge DOM and generated production bundle.
- Produces: verified desktop/mobile visual evidence and durable task closeout notes; no new runtime interface.

- [ ] **Step 1: Run actual desktop Browser QA**

Open the actual Streamlit app, select `심리 · Sentiment`, and expand `상세 근거와 원본 데이터`.

Verify with DOM measurements and a screenshot:

- CNN badge count equals the CNN component count.
- Every badge retains non-empty state text.
- Present snapshot tones have distinct foreground/background/border values.
- Numeric scores keep the existing neutral color.
- AAII rows have no CNN badge class.
- The disclosure and page have zero horizontal overflow.

- [ ] **Step 2: Run narrow mobile Browser QA**

Set a temporary `420 × 900` viewport, reload the actual app, reopen the sentiment disclosure, and verify:

- CNN evidence and AAII comparison stack in one column.
- Badges remain inside the CNN card and rating text is readable.
- Page, Streamlit main content, and component each have equal client/scroll widths.
- Save `overview-sentiment-cnn-status-badges-qa.png`, then reset the temporary viewport.

- [ ] **Step 3: Synchronize the active task records**

Append concise facts:

```markdown
- CNN component rating now uses the existing server tone as a compact badge; React does not duplicate score thresholds.
- Actual desktop/mobile QA confirmed readable state text, distinct present-state treatments, unchanged AAII rows, and zero horizontal overflow.
- QA screenshot `overview-sentiment-cnn-status-badges-qa.png` is generated and excluded from commits.
```

Update the focused regression count from `24` to `25` only after the full focused suite passes.

- [ ] **Step 4: Run final focused verification**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.OverviewAutomationContractTests.test_overview_sentiment_service_owns_implementation_body \
  tests.test_service_contracts.OverviewAutomationContractTests.test_overview_sentiment_entrypoint_uses_tab_helper_module \
  tests.test_service_contracts.OverviewAutomationContractTests.test_sentiment_react_component_scaffold_keeps_streamlit_fallback \
  tests.test_service_contracts.OverviewAutomationContractTests.test_sentiment_react_visual_hierarchy_uses_hero_and_balanced_current_evidence \
  tests.test_service_contracts.OverviewAutomationContractTests.test_sentiment_react_period_cards_watch_paths_and_detail_disclosure \
  tests.test_service_contracts.OverviewAutomationContractTests.test_sentiment_react_redesign_css_uses_balanced_surfaces_and_mobile_stack \
  tests.test_service_contracts.OverviewAutomationContractTests.test_sentiment_react_summary_surface_prioritizes_state_and_freshness \
  tests.test_service_contracts.OverviewAutomationContractTests.test_sentiment_react_driver_surface_groups_cnn_and_aaii_without_next_checks \
  tests.test_service_contracts.OverviewAutomationContractTests.test_sentiment_react_context_surface_shows_recent_range_and_divergence \
  tests.test_service_contracts.OverviewAutomationContractTests.test_sentiment_react_component_history_surface_shows_recent_changes \
  tests.test_service_contracts.OverviewAutomationContractTests.test_sentiment_react_evidence_surface_improves_graphs_and_raw_detail \
  tests.test_service_contracts.OverviewAutomationContractTests.test_sentiment_react_chart_tooltip_turns_inward_at_horizontal_edges \
  tests.test_service_contracts.OverviewAutomationContractTests.test_sentiment_react_cnn_component_ratings_use_tone_badges \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_aaii_direction_uses_spread_without_bearish_gate \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_sentiment_outlook_stays_unavailable_without_validated_estimator \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_sentiment_watch_conditions_publish_three_relationship_paths \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_sentiment_two_axis_cross_read_marks_cnn_fear_aaii_optimistic_as_divergent \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_sentiment_cross_read_matrix_handles_alignment_neutral_and_missing \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_sentiment_axes_include_aaii_long_term_comparison_and_history \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_sentiment_snapshot_exposes_full_aaii_responses \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_sentiment_snapshot_marks_missing_aaii_direction_and_responses_for_review \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_sentiment_snapshot_summarizes_cnn_and_aaii_context \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_sentiment_snapshot_adds_range_divergence_and_component_history \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_sentiment_react_payload_uses_existing_snapshot_fields \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_sentiment_payload_drops_unvalidated_demo_probabilities
```

Expected: `Ran 25 tests` and `OK`.

Then run:

```bash
cd app/web/streamlit_components/sentiment_workbench
npm run build
cd ../../../../
git diff --check
git status --short
```

Expected: build succeeds, `git diff --check` exits `0`, and only scoped implementation/docs plus known untracked research/mockup/QA artifacts are present.

- [ ] **Step 5: Commit the QA and documentation unit**

Stage only `STATUS.md`, `NOTES.md`, and `RUNS.md` from the active sentiment task.

```bash
git commit -m "Overview 심리 CNN 상태 배지 QA 기록"
```

Do not stage the QA screenshot, `.superpowers/`, unrelated research, or other existing untracked artifacts.
