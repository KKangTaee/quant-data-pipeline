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

export type EstimateStatus = "VERIFIED" | "PROVISIONAL" | "UNAVAILABLE";
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
  estimate_status: EstimateStatus;
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

export type ConditionalPathPoint = {
  step: number;
  x: number;
  y: number;
  lower_x: number;
  upper_x: number;
  lower_y: number;
  upper_y: number;
};

export type ConditionalPathPayload = {
  status: EstimateStatus;
  episode_count: number;
  band_label: string;
  points: ConditionalPathPoint[];
  terminal?: ConditionalPathPoint | null;
  validation?: Record<string, number | null>;
};

export type HorizonCard = {
  key: "current" | "5D" | "20D";
  label: string;
  kind: "observation" | "conditional_outlook";
  title: string;
  summary: string;
  estimate_status: EstimateStatus;
  edge_label: string;
  probabilities?: ProbabilityRow[];
  episode_count?: number;
  status_reason?: string;
  conditional_path?: ConditionalPathPayload;
};

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
  outlook: { five_day: string; twenty_day: string };
  change_condition: string;
  estimate_status: EstimateStatus;
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
  schema_version: "futures_macro_react_workbench_v2";
  component: "FuturesMacroWorkbench";
  command: CommandPayload;
  hero: HeroPayload;
  horizons: HorizonCard[];
  pattern_map: PatternMapPayload;
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
