export type SignalLevel = "support" | "neutral" | "watch" | "limited";

export type EvidenceRow = {
  key: string;
  label: string;
  status: "READY" | "PARTIAL" | "UNAVAILABLE";
  title: string;
  detail: string;
  as_of_date: string | null;
  signal_level: SignalLevel;
  signal_label: string;
  risk_label: string;
  data_quality_label: string;
};

export type PortfolioCurveRow = {
  date: string;
  unit_value: number;
  total_value: number | null;
  cumulative_return: number;
};

export type CurveMetadata = {
  interval: "daily";
  price_basis: "stored_close";
  aggregation: "none";
  intraday: false;
  observation_count: number;
  start_date: string | null;
  end_date: string | null;
};

export type TodayHeader = {
  as_of_date: string | null;
  source_count: number;
  source_ready_count: number;
  source_available_count: number;
  status: string;
  status_label: string;
};

export type TodayEvent = {
  date: string | null;
  days_until: number;
  type: string;
  title: string;
  importance: string;
};

export type TodayPayload = {
  schema_version: "today_home_v2";
  header: TodayHeader;
  market: {
    status: string;
    tone: string;
    headline: string;
    summary: string;
    evidence: EvidenceRow[];
    next_event: TodayEvent | null;
    watch_items: string[];
  };
  portfolio: {
    status: string;
    name: string;
    basis_date: string | null;
    summary: string;
    metrics: {
      current_value: number | null;
      latest_observation_return: number | null;
      return_from_date: string | null;
      return_to_date: string | null;
      total_return: number | null;
    };
    curve: PortfolioCurveRow[];
    curve_metadata: CurveMetadata;
    contributors: Array<{ symbol: string; value: number; tone: string }>;
    review_items: Array<{ severity: string; meaning: string }>;
    active_item_count: number;
  };
};

export type TodayEventId =
  | "open_market_research"
  | "open_stock_research"
  | "open_portfolio_monitoring";
