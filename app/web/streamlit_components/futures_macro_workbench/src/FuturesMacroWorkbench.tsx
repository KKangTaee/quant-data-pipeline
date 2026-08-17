import React, { useEffect, useState } from "react";
import { Streamlit, withStreamlitConnection, ComponentProps } from "streamlit-component-lib";
import CalculationTraceDisclosure from "./CalculationTraceDisclosure";
import FamilyDirectionSection from "./FamilyDirectionSection";
import MacroContextSection from "./MacroContextSection";
import MarketRepricingSection from "./MarketRepricingSection";
import MethodDisclosure from "./MethodDisclosure";
import PatternRibbonSection from "./PatternRibbonSection";
import ShortHorizonDecisionSection from "./ShortHorizonDecisionSection";
import type { ObservationStatus } from "./presentation";
import type {
  CommandPayload,
  FuturesMacroAction,
  HeroPayload,
  SessionEvidence,
} from "./contracts";
import "./style.css";

export type PublicationStatus = "VERIFIED" | "PROVISIONAL" | "NO_EDGE" | "UNAVAILABLE";
export type EstimateStatus = PublicationStatus;
export type { ObservationStatus } from "./presentation";
export type RegimeKey = "risk_seeking" | "defensive" | "inflation_rate_pressure" | "mixed";

export type {
  CommandPayload,
  FuturesMacroAction,
  HeroPayload,
  SessionEvidence,
} from "./contracts";

export type ProbabilityRow = {
  key: RegimeKey;
  label: string;
  value: number;
  baseline: number;
  lift: number;
};

export type TerminalRegion = {
  mass: number;
  center_x: number;
  center_y: number;
  radius_major: number;
  radius_minor: number;
  rotation_deg: number;
};

export type DirectionVector = {
  median_dx: number;
  median_dy: number;
  lower_dx: number;
  upper_dx: number;
  lower_dy: number;
  upper_dy: number;
};

type HorizonCardBase = {
  label: string;
  title: string;
  summary: string;
  edge_label: string;
  episode_count?: number;
  status_reason?: string;
};

export type ObservationHorizonCard = HorizonCardBase & {
  key: "current";
  kind: "observation";
  observation_status: ObservationStatus;
};

export type OutlookHorizonCard = HorizonCardBase & {
  key: "5D" | "20D";
  kind: "conditional_outlook";
  probability_status: PublicationStatus;
  coordinate_status: PublicationStatus;
  vector_status: PublicationStatus;
  probabilities: ProbabilityRow[];
  disclosure_probabilities: ProbabilityRow[];
  baseline_label?: string;
  selected_candidate?: string | null;
  terminal_regions: TerminalRegion[];
  direction_vector?: DirectionVector | null;
  macro_adjustment: { used: boolean; candidate?: string | null; reason: string };
};

export type HorizonCard = ObservationHorizonCard | OutlookHorizonCard;

export type PatternPoint = {
  date: string;
  x: number;
  y: number;
  regime: RegimeKey;
  regime_label: string;
  transition?: string;
  transition_label: string;
};

export type PatternMapPayload = {
  title: string;
  x_label: string;
  y_label: string;
  domain: { x: [number, number]; y: [number, number] };
  path: PatternPoint[];
};

export type EvidenceGroup = {
  key: "current" | "transition" | "outlook" | "invalidate";
  label: string;
  items: string[];
};

export type EvidencePayload = { title: string; groups: EvidenceGroup[] };

export type RibbonItem = {
  date: string;
  regime: RegimeKey;
  regime_label: string;
  transition: string;
  transition_label: string;
};

export type RibbonPayload = { title: string; items: RibbonItem[] };

export type DirectionState = {
  label: string;
  semantic_label: string;
  tone: "positive" | "negative" | "neutral" | "unavailable";
  value: number | null;
};

export type FamilyDirectionRow = {
  key: "risk_on" | "growth" | "rate_pressure" | "dollar_pressure" | "safe_haven" | "inflation_pressure";
  label: string;
  one_day: DirectionState;
  five_day: DirectionState;
  twenty_day: DirectionState;
  status: string;
};

export type ObservationCard = {
  key: "1D" | "5D" | "20D";
  title: string;
  summary: string;
};

export type CalculationScope = {
  collected_count: number;
  direct_family_input_count: number;
  available_family_count: number;
  required_family_count: number;
  shared_context_symbols: string[];
  raw_observation_symbols: string[];
};

export type MarketRepricingStatus = "ALIGNED" | "MIXED" | "SINGLE_AXIS" | "NEW_SHOCK" | "LOW_SIGNAL" | "UNAVAILABLE";

export type MarketRepricingPayload = {
  status: MarketRepricingStatus;
  confidence_label: string;
  headline: string;
  interpretation: string;
  supporting_evidence: string[];
  counter_evidence: string[];
  conditional_scenario: {
    summary: string;
    continuation_condition: string;
    invalidation_condition: string;
    sensitive_assets: string[];
  };
};

export type ShortHorizonDecisionPayload = {
  observation_cards: ObservationCard[];
  current_summary: string;
  one_day_shock: { title: string; summary: string };
  five_day_direction: { title: string; summary: string };
  twenty_day_background: { title: string; summary: string };
  market_repricing: MarketRepricingPayload;
  core_directions: FamilyDirectionRow[];
  confirmation_signals: FamilyDirectionRow[];
  confirmation_summary: string;
  change_conditions: string[];
  calculation_scope: CalculationScope;
};

export type AssetPathwayPayload = {
  key: "risk_assets" | "rates" | "dollar" | "safe_haven" | "commodities";
  label: string;
  current: { one_day: string; five_day: string; twenty_day: string };
  outlook: {
    five_day: string;
    five_day_status: EstimateStatus;
    twenty_day: string;
    twenty_day_status: EstimateStatus;
  };
  change_condition: string;
  observation_status: ObservationStatus;
};

export type MethodPayload = {
  source: string;
  effective_episodes: string;
  brier: string;
  baseline_brier: string;
  calibration: string;
  caveats: string[];
};

export type CalculationTraceValue = string | number | boolean | null;
export type CalculationTraceTable = {
  key: "scores" | "components" | "symbols";
  label: string;
  columns: string[];
  rows: Array<Record<string, CalculationTraceValue>>;
};
export type CalculationTracePayload = {
  metadata: Array<{ label: string; value: string }>;
  tables: CalculationTraceTable[];
  cautions: string[];
};

export type FuturesMacroWorkbenchPayload = {
  schema_version: "futures_macro_react_workbench_v7";
  component: "FuturesMacroWorkbench";
  command: CommandPayload;
  hero: HeroPayload;
  short_horizon_decision: ShortHorizonDecisionPayload;
  horizons: HorizonCard[];
  pattern_map: PatternMapPayload;
  session_evidence: SessionEvidence;
  evidence: EvidencePayload;
  ribbon: RibbonPayload;
  asset_pathways: AssetPathwayPayload[];
  method: MethodPayload;
  calculation_trace: CalculationTracePayload;
  action_boundary: "python_dispatch_only";
  boundary_note: string;
};

type Props = ComponentProps & { args: { payload?: FuturesMacroWorkbenchPayload } };

function syncFrameHeightSoon() {
  Streamlit.setFrameHeight();
  window.requestAnimationFrame(() => Streamlit.setFrameHeight());
  window.setTimeout(() => Streamlit.setFrameHeight(), 180);
}

function FuturesMacroWorkbench({ args }: Props) {
  const payload = args.payload;
  const [pendingActionId, setPendingActionId] = useState("");

  useEffect(() => {
    syncFrameHeightSoon();
  });

  if (!payload || payload.component !== "FuturesMacroWorkbench") {
    return null;
  }

  const emitAction = (action: FuturesMacroAction) => {
    setPendingActionId(action.id);
    Streamlit.setComponentValue({ event: { id: action.id, nonce: Date.now() } });
    window.setTimeout(() => setPendingActionId(""), 900);
  };

  return (
    <main
      className="fm-workbench"
      data-action-boundary={payload.action_boundary}
      data-schema-version={payload.schema_version}
    >
      <MacroContextSection
        command={payload.command}
        hero={payload.hero}
        onAction={emitAction}
        pendingActionId={pendingActionId}
        sessionEvidence={payload.session_evidence}
      />
      <ShortHorizonDecisionSection decision={payload.short_horizon_decision} />
      <MarketRepricingSection radar={payload.short_horizon_decision.market_repricing} />
      <FamilyDirectionSection
        coreDirections={payload.short_horizon_decision.core_directions}
        confirmationSignals={payload.short_horizon_decision.confirmation_signals}
        confirmationSummary={payload.short_horizon_decision.confirmation_summary}
      />
      <PatternRibbonSection ribbon={payload.ribbon} />
      <MethodDisclosure
        boundaryNote={payload.boundary_note}
        method={payload.method}
        onToggle={syncFrameHeightSoon}
        scope={payload.short_horizon_decision.calculation_scope}
      />
      <CalculationTraceDisclosure
        trace={payload.calculation_trace}
        onToggle={syncFrameHeightSoon}
      />
    </main>
  );
}

export default withStreamlitConnection(FuturesMacroWorkbench);
