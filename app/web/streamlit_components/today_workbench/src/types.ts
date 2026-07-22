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

export type PortfolioMetrics = {
  current_value: number | null;
  latest_observation_return: number | null;
  return_from_date: string | null;
  return_to_date: string | null;
  total_return: number | null;
};

export type PortfolioContributor = {
  symbol: string;
  contribution_value: number;
  value?: number;
  total_return: number | null;
  tone: "positive" | "negative";
};

export type PortfolioLiveStatus = "INACTIVE" | "LIVE_READY" | "LIVE_PARTIAL" | "EOD_WAITING";

export type PortfolioLivePoint = PortfolioCurveRow & {
  timestamp_utc: string;
  kind: "intraday";
};

export type PortfolioLive = {
  status: PortfolioLiveStatus;
  label: string;
  as_of_utc: string | null;
  trade_date: string | null;
  coverage: { fresh: number; expected: number; fallback_symbols: string[] };
  metrics: PortfolioMetrics | null;
  contributors: PortfolioContributor[];
  curve_point: PortfolioLivePoint | null;
  message: string;
};

export type TodayPortfolio = {
  status: string;
  name: string;
  basis_date: string | null;
  summary: string;
  metrics: PortfolioMetrics;
  curve: PortfolioCurveRow[];
  curve_metadata: CurveMetadata;
  contributors: PortfolioContributor[];
  review_items: Array<{ severity: string; meaning: string }>;
  active_item_count: number;
  live: PortfolioLive;
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

export type MarketSessionDay = {
  trade_date: string;
  day_kind: "TRADING_DAY" | "HOLIDAY" | "WEEKEND";
  holiday_label: string | null;
  open_at_utc: string | null;
  close_at_utc: string | null;
  is_early_close: boolean;
};

export type MarketSessionPayload = {
  schema_version: "market_session_v1";
  generated_at_utc: string;
  timezones: {
    market: "America/New_York";
    viewer: "Asia/Seoul";
  };
  calendar_quality: "CONFIRMED" | "LIMITED";
  warnings: string[];
  schedule: MarketSessionDay[];
};

export type MarketSessionPhase =
  | "PRE_OPEN"
  | "OPEN"
  | "CLOSED"
  | "HOLIDAY"
  | "WEEKEND"
  | "STALE";

export type TodayPayload = {
  schema_version: "today_home_v4";
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
  market_session: MarketSessionPayload;
  portfolio: TodayPortfolio;
};

export type TodayEventId =
  | "open_market_research"
  | "open_stock_research"
  | "open_portfolio_monitoring";
