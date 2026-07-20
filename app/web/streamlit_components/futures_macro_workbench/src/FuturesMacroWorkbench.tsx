import React, { useEffect, useState } from "react";
import { Streamlit, withStreamlitConnection, ComponentProps } from "streamlit-component-lib";
import AssetPathwaysSection from "./AssetPathwaysSection";
import CalculationTraceDisclosure from "./CalculationTraceDisclosure";
import CurrentEvidencePanel from "./CurrentEvidencePanel";
import MacroContextSection from "./MacroContextSection";
import MethodDisclosure from "./MethodDisclosure";
import PatternHorizonSection from "./PatternHorizonSection";
import PatternMapSection from "./PatternMapSection";
import PatternRibbonSection from "./PatternRibbonSection";
import "./style.css";

export type PublicationStatus = "VERIFIED" | "PROVISIONAL" | "NO_EDGE" | "UNAVAILABLE";
export type EstimateStatus = PublicationStatus;
export type ObservationStatus = "OBSERVED" | "PARTIAL" | "UNAVAILABLE";
export const OBSERVATION_LABEL: Record<ObservationStatus, string> = {
  OBSERVED: "관측 완료",
  PARTIAL: "일부 관측",
  UNAVAILABLE: "관측 불가",
};
export type RegimeKey = "risk_seeking" | "defensive" | "inflation_rate_pressure" | "mixed";

export type FuturesMacroAction = {
  id: "daily_refresh" | "reload";
  label: string;
  kind: "primary" | "secondary";
  detail?: string;
};

export type CommandPayload = {
  title: string;
  detail: string;
  actions: FuturesMacroAction[];
};

export type HeroPayload = {
  kicker: string;
  title: string;
  transition_label: string;
  summary: string;
  today_summary?: string;
  as_of_date: string;
  observation_status: ObservationStatus;
  coverage_label: string;
  evidence: string[];
};

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
  schema_version: "futures_macro_react_workbench_v3";
  component: "FuturesMacroWorkbench";
  command: CommandPayload;
  hero: HeroPayload;
  horizons: HorizonCard[];
  pattern_map: PatternMapPayload;
  session_evidence: {
    latest_final_session?: string | null;
    pending_session?: string | null;
    status?: string | null;
  };
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
      />
      <PatternHorizonSection horizons={payload.horizons} />
      <div className="fm-workbench__pattern-layout">
        <PatternMapSection patternMap={payload.pattern_map} horizons={payload.horizons} />
        <CurrentEvidencePanel evidence={payload.evidence} />
      </div>
      <PatternRibbonSection ribbon={payload.ribbon} />
      <AssetPathwaysSection pathways={payload.asset_pathways} />
      <MethodDisclosure
        boundaryNote={payload.boundary_note}
        horizons={payload.horizons}
        method={payload.method}
        onToggle={syncFrameHeightSoon}
      />
      <CalculationTraceDisclosure
        trace={payload.calculation_trace}
        onToggle={syncFrameHeightSoon}
      />
    </main>
  );
}

export default withStreamlitConnection(FuturesMacroWorkbench);
