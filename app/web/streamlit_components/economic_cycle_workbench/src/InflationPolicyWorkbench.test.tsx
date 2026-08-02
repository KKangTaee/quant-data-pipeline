import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { EconomicCycleWorkbenchView } from "./EconomicCycleWorkbench";
import InflationPolicyWorkbench from "./InflationPolicyWorkbench";
import type { InflationPolicyPayload } from "./inflationPolicyTypes";

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

function readyPayload(): InflationPolicyPayload {
  return {
    ...cyclePayload.inflation_policy,
    publication_status: "READY",
    headline: {
      ...cyclePayload.inflation_policy.headline,
      summary: "고착이 우세하지만 다음 발표에 따라 인상 경로가 달라집니다.",
    },
    inflation: {
      publication_status: "READY",
      reason: "검증된 연말 경로",
      q4_quantiles_pct: { p05: 2.8, p20: 3.1, p50: 3.4, p80: 3.7, p95: 4.0 },
      state_probabilities: {
        rapid_disinflation: 0.1,
        gradual_disinflation: 0.2,
        sticky: 0.4,
        reacceleration: 0.2,
        shock_reacceleration: 0.1,
      },
      state_rows: [
        { id: "rapid_disinflation", label: "빠른 둔화", probability: 0.1 },
        { id: "gradual_disinflation", label: "완만한 둔화", probability: 0.2 },
        { id: "sticky", label: "고착", probability: 0.4 },
        { id: "reacceleration", label: "재가속", probability: 0.2 },
        { id: "shock_reacceleration", label: "충격성 재가속", probability: 0.1 },
      ],
      threshold_probabilities: { "3.4000": 0.5, "3.5000": 0.4, "3.6000": 0.3 },
      next_release_scenarios: [0.1, 0.2, 0.3, 0.4, 0.5].map((mom) => ({
        mom_pct: mom,
        publication_status: "READY" as const,
        reacceleration_delta: (mom - 0.3) * 0.5,
        hike_delta: (mom - 0.3) * 0.4,
      })),
      state_definition: { definition_version: "sep-20260617-v1" },
    },
    policy: {
      publication_status: "READY",
      reason: "검증된 정책 경로",
      next_meeting_probabilities: { cut: 0.1, hold: 0.6, hike: 0.3 },
      net_move_probabilities: {
        cut_1: 0.05,
        cut_2: 0.02,
        cut_3_plus: 0.01,
        hold: 0.32,
        hike_1: 0.2,
        hike_2: 0.25,
        hike_3_plus: 0.15,
      },
      year_end_target_probabilities: { "3.6250": 0.32, "3.8750": 0.2, "4.1250": 0.25, ">=4.3750": 0.23 },
      committee_vote_prior: { cut: 0.0, hold: 0.7, hike: 0.3 },
      sep_net_move_prior: { hold: 0.4, hike_1: 0.2, hike_2: 0.3, hike_3_plus: 0.1 },
    },
    rates: {
      publication_status: "READY",
      reason: "검증된 금리 경로",
      ten_year: { current_value_pct: 4.65, observation_date: "2026-08-01" },
      instruments: {},
      driver_decomposition: {
        dominant_driver: "real_growth_driven",
        policy_term_lens: { two_year_policy_proxy_change_bp: 24, term_premium_change_bp: null },
        real_inflation_lens: { real_10y_change_bp: 26, breakeven_10y_change_bp: -2, identity_gap_bp: 3 },
      },
      inflation_confirmation: { status: "MIXED", reason: "split_lenses" },
      term_premium_status: "NOT_AVAILABLE",
      resistance_zones: [
        {
          definition_id: "auto-1",
          owner: "AUTO",
          owner_label: "자동 추천",
          definition_name: "현재 자동 저항 구간",
          instrument: "DGS10",
          zone_lower_pct: 4.58,
          zone_upper_pct: 4.65,
          buffer_pct: 0.05,
          confirmation_profile: {},
          known_at: "2026-07-16",
          algorithm_version: "yield-zone-v1",
          state: "ATTEMPT",
          zone_strength: 7.9,
          timeframes: [63, 252, 504],
          source: "SNAPSHOT_AUTO",
          editable: false,
        },
        {
          definition_id: "user-1",
          owner: "USER",
          owner_label: "사용자 기준",
          definition_name: "내 4.7 기준",
          instrument: "DGS10",
          zone_lower_pct: 4.68,
          zone_upper_pct: 4.75,
          buffer_pct: 0.05,
          short_lookback_days: 63,
          long_lookback_days: 504,
          confirmation_profile: {},
          known_at: "2026-08-01",
          saved_at: "2026-08-01",
          algorithm_version: "user-resistance-criterion-v1",
          state: null,
          zone_strength: null,
          timeframes: [],
          source: "SAVED",
          editable: true,
        },
      ],
    },
  };
}

describe("inflation policy inner navigation", () => {
  it("keeps 경기 국면 as default and opens 물가·정책 경로 explicitly", async () => {
    render(<EconomicCycleWorkbenchView payload={cyclePayload} onCommand={vi.fn()} />);

    expect(screen.getByRole("heading", { name: /현재와 앞으로 1·2개월/ })).toBeInTheDocument();
    await userEvent.click(screen.getByRole("tab", { name: "물가·정책 경로" }));
    expect(screen.getByRole("heading", { name: /연말 Core PCE 경로/ })).toBeInTheDocument();
  });
});

describe("forward inflation policy decision flow", () => {
  it("shows five states, thresholds, next prints, policy bins, and criterion owners", () => {
    render(<InflationPolicyWorkbench payload={readyPayload()} onCommand={vi.fn()} />);

    for (const label of ["빠른 둔화", "완만한 둔화", "고착", "재가속", "충격성 재가속"]) {
      expect(screen.getAllByText(label).length).toBeGreaterThan(0);
    }
    expect(screen.getByText("5상태 합계 100%" )).toBeInTheDocument();
    for (const threshold of ["3.4%", "3.5%", "3.6%"]) {
      expect(screen.getByText(threshold)).toBeInTheDocument();
    }
    for (const nextPrint of ["0.1%", "0.2%", "0.3%", "0.4%", "0.5%"]) {
      expect(screen.getByRole("row", { name: new RegExp(`Core PCE ${nextPrint.replace(".", "\\.")}`) })).toBeInTheDocument();
    }
    for (const path of ["동결", "1회 인상", "2회 인상", "3회 이상 인상"]) {
      expect(screen.getAllByText(path).length).toBeGreaterThan(0);
    }
    expect(screen.getAllByText("자동 추천").length).toBeGreaterThan(0);
    expect(screen.getByText("사용자 기준")).toBeInTheDocument();
    expect(screen.queryByText(/저장 rows|실행 job|실패 job/)).not.toBeInTheDocument();
  });

  it("keeps missing term premium explicit and labels mixed inflation confirmation", () => {
    render(<InflationPolicyWorkbench payload={readyPayload()} onCommand={vi.fn()} />);

    expect(screen.getByText("기간 프리미엄 자료 없음")).toBeInTheDocument();
    expect(screen.getByText("혼합")).toBeInTheDocument();
    expect(screen.getByText("실질금리·성장 주도")).toBeInTheDocument();
  });
});

describe("reverse target and saved criterion workflow", () => {
  it("submits a conditional target instead of a required hike scalar", async () => {
    const onCommand = vi.fn();
    render(<InflationPolicyWorkbench payload={readyPayload()} onCommand={onCommand} />);

    await userEvent.selectOptions(screen.getByLabelText("금리 종류"), "DGS10");
    await userEvent.clear(screen.getByLabelText("구간 하단"));
    await userEvent.type(screen.getByLabelText("구간 하단"), "4.68");
    await userEvent.clear(screen.getByLabelText("구간 상단"));
    await userEvent.type(screen.getByLabelText("구간 상단"), "4.75");
    await userEvent.click(screen.getByRole("button", { name: "필요 경로 역산" }));

    expect(onCommand.mock.calls[0][0].id).toBe("run_reverse_scenario");
    expect(onCommand.mock.calls[0][0].payload).toMatchObject({
      instrument: "DGS10",
      zone_lower_pct: 4.68,
      zone_upper_pct: 4.75,
      condition: "CONFIRMED",
    });
    expect(onCommand.mock.calls[0][0].payload).not.toHaveProperty("required_hike_count");
  });

  it("disables reverse submission when target bounds are invalid", async () => {
    render(<InflationPolicyWorkbench payload={readyPayload()} onCommand={vi.fn()} />);

    await userEvent.clear(screen.getByLabelText("구간 하단"));
    await userEvent.type(screen.getByLabelText("구간 하단"), "5.10");
    await userEvent.clear(screen.getByLabelText("구간 상단"));
    await userEvent.type(screen.getByLabelText("구간 상단"), "4.70");

    expect(screen.getByRole("button", { name: "필요 경로 역산" })).toBeDisabled();
    expect(screen.getByText("구간 하단은 상단보다 낮아야 합니다.")).toBeInTheDocument();
  });

  it("copies an automatic zone into a separately owned user definition", async () => {
    const onCommand = vi.fn();
    render(<InflationPolicyWorkbench payload={readyPayload()} onCommand={onCommand} />);

    expect(screen.queryByRole("button", { name: "자동 기준 수정" })).not.toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "사용자 기준으로 복사" }));
    await userEvent.clear(screen.getByLabelText("기준 이름"));
    await userEvent.type(screen.getByLabelText("기준 이름"), "내 장기금리 기준");
    await userEvent.click(screen.getByRole("button", { name: "사용자 기준 저장" }));

    expect(onCommand.mock.calls[0][0].id).toBe("save_yield_criterion");
    expect(onCommand.mock.calls[0][0].payload).toMatchObject({
      owner: "USER",
      definition_name: "내 장기금리 기준",
      instrument: "DGS10",
    });
  });

  it("shows an unavailable reverse reason without inventing a required path", () => {
    render(<InflationPolicyWorkbench payload={readyPayload()} onCommand={vi.fn()} />);

    expect(screen.getByText("공동 경로 검증 전")).toBeInTheDocument();
    expect(screen.getByText(/구간을 넓히거나 horizon을 늘린 뒤/)).toBeInTheDocument();
    expect(screen.queryByText(/필요 인상 횟수: [0-9]/)).not.toBeInTheDocument();
  });
});
