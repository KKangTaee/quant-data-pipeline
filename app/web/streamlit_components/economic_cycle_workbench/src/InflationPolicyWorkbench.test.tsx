import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { EconomicCycleWorkbenchView } from "./EconomicCycleWorkbench";

const cyclePayload = {
  schema_version: "economic_cycle_v2" as const,
  status: "READY" as const,
  as_of_date: "2026-08-02",
  model_version: "cycle-v2",
  headline: { phase: "expansion" as const, phase_label: "확장", summary: "확장 우세" },
  horizons: [
    {
      horizon_months: 0 as const,
      label: "현재",
      probabilities: { recovery: 0.1, expansion: 0.6, slowdown: 0.2, recession: 0.1 },
      dominant_phase: "expansion" as const,
      dominant_phase_label: "확장",
      confidence: 0.6,
      publication_status: "READY" as const,
      estimate_status: "VERIFIED" as const,
    },
  ],
  evidence: [],
  market_implications: [],
  history: [],
  limitations: [],
  inflation_policy: {
    schema_version: "inflation_policy_v1" as const,
    publication_status: "NOT_AVAILABLE" as const,
    as_of_at: "2026-08-02T00:00:00Z",
    model_version: "inflation-policy-v1",
    headline: {
      title: "연말 Core PCE 경로와 정책·금리 조건",
      summary: "공동 경로 검증 전입니다.",
      is_historical: false,
      history_label: "현재 기준",
      run_kind: "current",
    },
    inflation: {
      publication_status: "NOT_AVAILABLE" as const,
      reason: "검증 전",
      q4_quantiles_pct: {},
      state_probabilities: {},
      state_rows: [],
      threshold_probabilities: {},
      next_release_scenarios: [],
      state_definition: {},
    },
    policy: {
      publication_status: "NOT_AVAILABLE" as const,
      reason: "검증 전",
      next_meeting_probabilities: {},
      net_move_probabilities: {},
      year_end_target_probabilities: {},
      committee_vote_prior: {},
      sep_net_move_prior: {},
    },
    rates: {
      publication_status: "NOT_AVAILABLE" as const,
      reason: "검증 전",
      ten_year: {},
      instruments: {},
      driver_decomposition: {},
      inflation_confirmation: { status: "UNCONFIRMED", reason: "검증 전" },
      term_premium_status: "NOT_AVAILABLE" as const,
      resistance_zones: [],
    },
    reverse_scenario: { publication_status: "NOT_AVAILABLE" as const, reason: "검증 전" },
    equity_stress: { publication_status: "NOT_AVAILABLE" as const, reason: "4차" },
    recession: { publication_status: "NOT_AVAILABLE" as const, reason: "5차" },
    evidence: { items: [], details: {} },
    freshness: {},
    warnings: [],
  },
};

describe("inflation policy inner navigation", () => {
  it("keeps 경기 국면 as default and opens 물가·정책 경로 explicitly", async () => {
    render(<EconomicCycleWorkbenchView payload={cyclePayload} onCommand={vi.fn()} />);

    expect(screen.getByRole("heading", { name: /현재와 앞으로 1·2개월/ })).toBeInTheDocument();
    await userEvent.click(screen.getByRole("tab", { name: "물가·정책 경로" }));
    expect(screen.getByRole("heading", { name: /연말 Core PCE 경로/ })).toBeInTheDocument();
  });
});
