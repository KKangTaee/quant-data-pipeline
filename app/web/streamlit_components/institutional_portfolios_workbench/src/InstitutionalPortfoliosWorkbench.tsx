import React, { useEffect, useMemo, useRef, useState } from "react";
import { ComponentProps, Streamlit, withStreamlitConnection } from "streamlit-component-lib";
import "./style.css";

type ManagerItem = {
  cik: string | null;
  manager_name: string;
  latest_report_period: string;
  watchlist_label?: string | null;
  external_links?: Array<{ label: string; url: string }>;
  selected: boolean;
};

type Segment = {
  key: string;
  label: string;
  symbol?: string | null;
  issuer_name: string;
  weight_pct: number;
  weight_label: string;
  reported_value: number;
  value_label: string;
  color: string;
  drilldown_query: string;
};

type ChangeItem = {
  label: string;
  issuer_name: string;
  symbol?: string | null;
  weight_label: string;
  value_delta: number;
  value_delta_label: string;
  drilldown_query: string;
};

type ChangeGroup = {
  label: string;
  description: string;
  count: number;
  items: ChangeItem[];
};

type SectorBar = {
  sector: string;
  weight_pct: number;
  weight_label: string;
  value_label: string;
  holding_count: number;
  bar_width_pct: number;
  color: string;
};

type HoldingRow = {
  issuer_name: string;
  symbol?: string | null;
  cusip?: string | null;
  sector: string;
  weight_label: string;
  value_label: string;
  drilldown_query: string;
};

type InterestHolder = {
  manager_name: string;
  cik: string;
  period_of_report: string;
  filing_date: string;
  issuer_name: string;
  symbol?: string | null;
  cusip?: string | null;
  weight_label: string;
  value_label: string;
  source_ref?: string | null;
};

type ChartPoint = {
  date: string;
  price: number;
};

type PriceAction = {
  action_id: "collect_price_history" | string;
  label: string;
  symbol?: string | null;
  start_date?: string | null;
  available: boolean;
  needs_collection?: boolean;
  reason?: string;
};

type PriceRefreshResult = {
  symbol?: string | null;
  status?: string;
  message?: string;
  rows_written?: number;
  finished_at?: string | null;
};

type SelectedSecurity = {
  status?: "ok" | "empty" | string;
  query?: string;
  empty_text?: string;
  security?: {
    symbol?: string | null;
    issuer_name: string;
    cusip?: string | null;
    sector?: string | null;
    industry?: string | null;
  };
  portfolio_position?: {
    weight_label: string;
    value_label: string;
    shares_label: string;
  };
  charts?: Record<"daily" | "weekly" | "monthly", { label: string; points: ChartPoint[] }>;
  price_action?: PriceAction;
  holders?: InterestHolder[];
  holder_count?: number;
  caveat?: string;
};

type PerformanceRow = {
  symbol: string;
  issuer_name: string;
  weight_label: string;
  start_date: string;
  latest_date: string;
  return_pct: number;
  return_label: string;
  contribution_label: string;
  drilldown_query: string;
};

type PortfolioPerformance = {
  status: "ok" | "unavailable" | string;
  title?: string;
  report_period?: string | null;
  latest_price_date?: string | null;
  portfolio_return_label?: string;
  covered_weight_label?: string;
  reason?: string;
  rows?: PerformanceRow[];
  top_contributors?: PerformanceRow[];
  top_laggards?: PerformanceRow[];
  best_return?: PerformanceRow;
  caveat?: string;
};

type PopularityRow = {
  rank: number;
  report_period?: string | null;
  cusip?: string | null;
  symbol?: string | null;
  issuer_name: string;
  holder_count: number;
  holder_count_label: string;
  value_label: string;
  sample_managers: string;
  drilldown_query: string;
};

type PopularityPayload = {
  status: "ok" | "empty" | "not_loaded" | string;
  title: string;
  subtitle?: string;
  report_period?: string | null;
  rows: PopularityRow[];
  empty_text?: string;
  caveat?: string;
};

type WorkbenchPayload = {
  schema_version: "institutional_portfolios_workbench_v1";
  component: "InstitutionalPortfoliosWorkbench";
  mode: "live" | "preview" | string;
  data_state: {
    label: string;
    message: string;
    is_preview: boolean;
    as_of_label: string;
  };
  manager_picker: {
    selected_cik?: string | null;
    items: ManagerItem[];
  };
  freshness?: {
    status: string;
    last_collected_at?: string | null;
    latest_report_period?: string | null;
    latest_filing_date?: string | null;
    rows_written?: number;
    is_stale?: boolean;
    stale_reason?: string;
  };
  refresh_action?: {
    action_id: string;
    label: string;
    primary: boolean;
    description: string;
  };
  hero: {
    manager_name: string;
    cik?: string | null;
    latest_report_period: string;
    latest_filing_date: string;
    previous_report_period: string;
    total_reported_value_label: string;
    holding_count: number;
    source_ref?: string | null;
    facts: Array<{ label: string; value: string }>;
    caveat: string;
  };
  allocation: {
    title: string;
    subtitle: string;
    total_label: string;
    segments: Segment[];
    top_holdings: Segment[];
  };
  change_board: {
    title: string;
    subtitle: string;
    comparison_available?: boolean;
    empty_reason?: string;
    groups: Record<string, ChangeGroup>;
  };
  portfolio_performance?: PortfolioPerformance;
  sector_exposure: {
    title: string;
    subtitle: string;
    bars: SectorBar[];
  };
  holdings_table: {
    rows: HoldingRow[];
  };
  interest: {
    query: string;
    holder_count: number;
    holders: InterestHolder[];
    empty_text: string;
  };
  selected_security?: SelectedSecurity;
  security_charts?: Record<string, Record<"daily" | "weekly" | "monthly", { label: string; points: ChartPoint[] }>>;
  price_refresh_result?: PriceRefreshResult;
  popularity?: PopularityPayload;
  source_caveats: {
    visible: boolean;
    items: string[];
  };
  boundary: {
    recommendation: boolean;
    trade_signal: boolean;
    live_trading: boolean;
  };
};

type Props = ComponentProps & {
  args: {
    payload?: WorkbenchPayload;
  };
};

type ViewName = "overview" | "holdings" | "interest" | "popularity";

type PendingAction =
  | { kind: "manager"; cik: string; label: string }
  | { kind: "interest"; query: string; label: string }
  | { kind: "popularity"; label: string }
  | { kind: "price"; symbol: string; label: string }
  | { kind: "refresh"; label: string };

function syncFrameHeightSoon() {
  Streamlit.setFrameHeight();
  window.requestAnimationFrame(() => Streamlit.setFrameHeight());
  window.setTimeout(() => Streamlit.setFrameHeight(), 180);
}

function hostScrollPosition() {
  try {
    return { x: window.parent.scrollX, y: window.parent.scrollY };
  } catch {
    return { x: window.scrollX, y: window.scrollY };
  }
}

function restoreHostScroll(position: { x: number; y: number }) {
  const restore = () => {
    try {
      window.parent.scrollTo(position.x, position.y);
    } catch {
      window.scrollTo(position.x, position.y);
    }
  };
  window.requestAnimationFrame(restore);
  window.setTimeout(restore, 80);
  window.setTimeout(restore, 220);
}

function clampPercent(value: number | string | undefined) {
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) {
    return 0;
  }
  return Math.max(0, Math.min(100, numeric));
}

function arcPath(startAngle: number, endAngle: number, radius: number) {
  const start = polarToCartesian(radius, endAngle);
  const end = polarToCartesian(radius, startAngle);
  const largeArcFlag = endAngle - startAngle <= 180 ? "0" : "1";
  return `M ${start.x} ${start.y} A ${radius} ${radius} 0 ${largeArcFlag} 0 ${end.x} ${end.y}`;
}

function polarToCartesian(radius: number, angleInDegrees: number) {
  const angleInRadians = ((angleInDegrees - 90) * Math.PI) / 180;
  return {
    x: 100 + radius * Math.cos(angleInRadians),
    y: 100 + radius * Math.sin(angleInRadians),
  };
}

function AllocationDonut({ segments }: { segments: Segment[] }) {
  const total = segments.reduce((sum, item) => sum + Math.max(0, Number(item.weight_pct) || 0), 0);
  let cursor = 0;
  const arcs = segments.map((segment) => {
    const share = total > 0 ? Math.max(0, segment.weight_pct) / total : 0;
    const start = cursor;
    const end = cursor + share * 360;
    cursor = end;
    return { segment, start, end };
  });

  return (
    <div className="ip-donut" aria-label="Portfolio allocation donut">
      <svg viewBox="0 0 200 200" role="img">
        <circle className="ip-donut__track" cx="100" cy="100" r="72" />
        {arcs.map(({ segment, start, end }) => {
          if (end - start <= 0.01) {
            return null;
          }
          return <path key={segment.key} d={arcPath(start, end, 72)} stroke={segment.color} className="ip-donut__arc" />;
        })}
      </svg>
      <div className="ip-donut__center">
        <strong>{segments[0]?.weight_label || "0.0%"}</strong>
        <span>{segments[0]?.label || "No holdings"}</span>
      </div>
    </div>
  );
}

function MiniLineChart({ points }: { points: ChartPoint[] }) {
  if (!points || points.length < 2) {
    return <div className="ip-chart-empty">가격 데이터 없음</div>;
  }
  const width = 520;
  const height = 180;
  const pad = 14;
  const prices = points.map((point) => Number(point.price)).filter((value) => Number.isFinite(value));
  const min = Math.min(...prices);
  const max = Math.max(...prices);
  const span = max - min || 1;
  const path = points
    .map((point, idx) => {
      const x = pad + (idx / Math.max(1, points.length - 1)) * (width - pad * 2);
      const y = height - pad - ((Number(point.price) - min) / span) * (height - pad * 2);
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");

  return (
    <div className="ip-mini-chart">
      <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label="저장 가격 차트">
        <line x1={pad} x2={width - pad} y1={height - pad} y2={height - pad} />
        <polyline points={path} />
      </svg>
      <div className="ip-mini-chart__axis">
        <span>{points[0]?.date}</span>
        <strong>{points[points.length - 1]?.price?.toFixed?.(2) || points[points.length - 1]?.price}</strong>
        <span>{points[points.length - 1]?.date}</span>
      </div>
    </div>
  );
}

function PortfolioPerformancePanel({
  performance,
  onDrilldown,
}: {
  performance?: PortfolioPerformance;
  onDrilldown: (query: string) => void;
}) {
  const rows = performance?.rows || [];
  return (
    <div className="ip-panel ip-performance-panel">
      <div className="ip-section-head">
        <div>
          <h3>{performance?.title || "보고 기준일 이후 가정 성과"}</h3>
          <p>
            {performance?.status === "ok"
              ? `${performance.report_period || "-"}부터 ${performance.latest_price_date || "-"}까지 저장 가격 기준`
              : performance?.reason || "가격 DB coverage가 없어 계산하지 못했습니다."}
          </p>
        </div>
        <strong>{performance?.status === "ok" ? performance.portfolio_return_label : "-"}</strong>
      </div>
      <div className="ip-performance-metrics">
        <div>
          <span>가격 커버리지</span>
          <strong>{performance?.covered_weight_label || "-"}</strong>
        </div>
        <div>
          <span>최고 수익률</span>
          <strong>{performance?.best_return?.return_label || "-"}</strong>
        </div>
        <div>
          <span>대상 종목</span>
          <strong>{rows.length.toLocaleString()}</strong>
        </div>
      </div>
      <div className="ip-performance-list">
        {rows.slice(0, 8).map((row) => (
          <button type="button" key={`${row.symbol}-${row.start_date}`} onClick={() => onDrilldown(row.drilldown_query)}>
            <span>
              <strong>{row.symbol}</strong>
              <small>{row.issuer_name}</small>
            </span>
            <em>{row.return_label}</em>
            <small>{row.contribution_label}</small>
          </button>
        ))}
      </div>
      <p className="ip-note">{performance?.caveat}</p>
    </div>
  );
}

function SecurityDetail({
  detail,
  interest,
  notice,
  priceRefresh,
  disabled,
  onCollectPrice,
}: {
  detail?: SelectedSecurity;
  interest: WorkbenchPayload["interest"];
  notice?: string | null;
  priceRefresh?: PriceRefreshResult;
  disabled?: boolean;
  onCollectPrice: (action: PriceAction) => void;
}) {
  const [chartMode, setChartMode] = useState<"daily" | "weekly" | "monthly">("daily");
  const charts = detail?.charts;
  const chart = charts?.[chartMode];
  const holders = detail?.holders?.length ? detail.holders : interest.holders;
  const holderCount = detail?.holder_count ?? interest.holder_count;
  const chartHasPoints = Boolean(chart?.points && chart.points.length >= 2);
  const priceAction = detail?.price_action;
  const selectedSymbol = String(detail?.security?.symbol || "").toUpperCase();
  const refreshSymbol = String(priceRefresh?.symbol || "").toUpperCase();
  const priceRefreshText =
    priceRefresh?.status && selectedSymbol && refreshSymbol === selectedSymbol
      ? `${priceRefresh.status === "success" || priceRefresh.status === "partial_success" ? "가격 데이터 수집 완료" : "가격 데이터 수집 결과"} · ${
          priceRefresh.rows_written?.toLocaleString?.() || 0
        } rows`
      : "";

  if (!interest.query && detail?.status !== "ok") {
    return <div className="ip-interest-empty">{interest.empty_text}</div>;
  }

  return (
    <div className="ip-security-detail">
      {notice ? <div className="ip-board-note">{notice}</div> : null}
      <div className="ip-security-detail__summary">
        <div>
          <span className="ip-security-detail__kicker">선택 종목</span>
          <h3>{detail?.security?.symbol || interest.query || "-"}</h3>
          <p>{detail?.security?.issuer_name || detail?.empty_text || interest.empty_text}</p>
        </div>
        <div className="ip-security-detail__stats">
          <div>
            <span>포트폴리오 비중</span>
            <strong>{detail?.portfolio_position?.weight_label || "-"}</strong>
          </div>
          <div>
            <span>보고 평가액</span>
            <strong>{detail?.portfolio_position?.value_label || "-"}</strong>
          </div>
          <div>
            <span>보유 기관</span>
            <strong>{holderCount.toLocaleString()}</strong>
          </div>
        </div>
      </div>
      <div className="ip-security-detail__body">
        <div className="ip-chart-panel">
          <div className="ip-chart-tabs">
            {(["daily", "weekly", "monthly"] as const).map((mode) => (
              <button
                key={mode}
                type="button"
                className={chartMode === mode ? "ip-chart-tabs__active" : ""}
                onClick={() => setChartMode(mode)}
              >
                {charts?.[mode]?.label || mode}
              </button>
            ))}
          </div>
          <MiniLineChart points={chart?.points || []} />
          {!chartHasPoints && priceAction?.available ? (
            <button type="button" className="ip-price-action" disabled={disabled} onClick={() => onCollectPrice(priceAction)}>
              {priceAction.label || "가격 데이터 수집"}
            </button>
          ) : null}
          {!chartHasPoints && priceAction?.reason ? <p className="ip-price-reason">{priceAction.reason}</p> : null}
          {priceRefreshText ? <p className="ip-price-result">{priceRefreshText}</p> : null}
          <p className="ip-note">{detail?.caveat}</p>
        </div>
        <div className="ip-holder-panel">
          <div className="ip-section-head">
            <div>
              <h3>보유 기관 리스트</h3>
              <p>저장된 최신 13F filing 기준입니다.</p>
            </div>
            <strong>{holderCount.toLocaleString()}</strong>
          </div>
          <div className="ip-interest-list">
            {holders.length ? (
              holders.slice(0, 24).map((holder) => (
                <a href={holder.source_ref || "#"} target="_blank" rel="noreferrer" key={`${holder.cik}-${holder.manager_name}`}>
                  <span>
                    <strong>{holder.manager_name}</strong>
                    <small>{holder.period_of_report} · 제출 {holder.filing_date}</small>
                  </span>
                  <em>{holder.weight_label}</em>
                  <small>{holder.value_label}</small>
                </a>
              ))
            ) : (
              <div className="ip-interest-empty">{interest.empty_text}</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function PopularityRankingPanel({
  popularity,
  onLoad,
  onDrilldown,
}: {
  popularity?: PopularityPayload;
  onLoad: () => void;
  onDrilldown: (query: string) => void;
}) {
  const rows = popularity?.rows || [];
  return (
    <section className="ip-panel">
      <div className="ip-section-head">
        <div>
          <h3>{popularity?.title || "기관 보유 랭킹"}</h3>
          <p>{popularity?.subtitle || "보고 기준 분기별로 많은 기관이 보유한 종목을 확인합니다."}</p>
        </div>
        <strong>{popularity?.report_period || "-"}</strong>
      </div>
      {popularity?.status === "not_loaded" ? (
        <button type="button" className="ip-load-button" onClick={onLoad}>
          기관 보유 랭킹 불러오기
        </button>
      ) : (
        <div className="ip-popularity-list">
          {rows.length ? (
            rows.map((row) => (
              <button type="button" key={`${row.rank}-${row.cusip}`} onClick={() => onDrilldown(row.drilldown_query)}>
                <strong>{row.rank}</strong>
                <span>
                  <b>{row.symbol || row.cusip || "-"}</b>
                  <small>{row.issuer_name}</small>
                </span>
                <em>{row.holder_count_label}개 기관</em>
                <small>{row.value_label}</small>
              </button>
            ))
          ) : (
            <div className="ip-interest-empty">{popularity?.empty_text || "랭킹 데이터가 없습니다."}</div>
          )}
        </div>
      )}
      <p className="ip-note">{popularity?.caveat}</p>
    </section>
  );
}

function InstitutionalPortfoliosWorkbench({ args }: Props) {
  const payload = args.payload;
  const [activeView, setActiveView] = useState<ViewName>("overview");
  const [pendingAction, setPendingAction] = useState<PendingAction | null>(null);
  const [actionNotice, setActionNotice] = useState<string | null>(null);
  const [localSelectedQuery, setLocalSelectedQuery] = useState<string>("");
  const managerRailRef = useRef<HTMLDivElement | null>(null);
  const managerRailScrollRef = useRef(0);

  useEffect(() => {
    Streamlit.setComponentReady();
    syncFrameHeightSoon();
  }, []);

  useEffect(() => {
    syncFrameHeightSoon();
  }, [payload, activeView]);

  useEffect(() => {
    const rail = managerRailRef.current;
    if (rail) {
      rail.scrollLeft = managerRailScrollRef.current;
    }
  }, [payload?.manager_picker.selected_cik, payload?.manager_picker.items.length]);

  useEffect(() => {
    if (!pendingAction || !payload) {
      return;
    }
    if (pendingAction.kind === "manager" && payload.manager_picker.selected_cik === pendingAction.cik) {
      setPendingAction(null);
      setActionNotice(null);
    }
    if (pendingAction.kind === "interest" && payload.interest.query === pendingAction.query) {
      setPendingAction(null);
      setActionNotice(null);
    }
    if (pendingAction.kind === "popularity" && payload.popularity?.status !== "not_loaded") {
      setPendingAction(null);
      setActionNotice(null);
    }
    if (
      pendingAction.kind === "price" &&
      String(payload.price_refresh_result?.symbol || "").toUpperCase() === pendingAction.symbol
    ) {
      setPendingAction(null);
      setActionNotice(null);
    }
  }, [payload, pendingAction]);

  useEffect(() => {
    if (!pendingAction) {
      return undefined;
    }
    const timer = window.setTimeout(() => {
      setActionNotice(
        pendingAction.kind === "interest"
          ? "서버 응답이 지연되어 우선 현재 포트폴리오 row 기준 상세를 표시합니다. 보유 기관 리스트는 응답이 오면 자동으로 갱신됩니다."
          : pendingAction.kind === "price"
            ? "가격 수집 응답이 지연되고 있습니다. 수집이 끝나면 차트가 자동으로 갱신됩니다."
          : "서버 응답이 지연되고 있습니다. 화면은 멈추지 않도록 로딩 표시를 해제했습니다."
      );
      setPendingAction(null);
    }, 7000);
    return () => window.clearTimeout(timer);
  }, [pendingAction]);

  const changeGroups = useMemo(() => {
    if (!payload) {
      return [];
    }
    return ["reported_new", "increased", "reduced", "no_longer_reported"].map((key) => ({
      key,
      ...payload.change_board.groups[key],
    }));
  }, [payload]);

  const localSecurityDetail = useMemo<SelectedSecurity | undefined>(() => {
    if (!payload || payload.selected_security?.status === "ok") {
      return payload?.selected_security;
    }
    const query = localSelectedQuery || payload.interest.query;
    if (!query) {
      return payload.selected_security;
    }
    const upper = query.toUpperCase();
    const row = payload.holdings_table.rows.find((item) => {
      const symbol = String(item.symbol || "").toUpperCase();
      const cusip = String(item.cusip || "").toUpperCase();
      const issuer = String(item.issuer_name || "").toUpperCase();
      return symbol === upper || cusip === upper || issuer.includes(upper);
    });
    if (!row) {
      return payload.selected_security;
    }
    const chartKey = String(row.symbol || "").toUpperCase();
    const fallbackCharts = chartKey ? payload.security_charts?.[chartKey] : undefined;
    const hasFallbackChart = Boolean(
      fallbackCharts && Object.values(fallbackCharts).some((item) => (item.points || []).length >= 2)
    );
    return {
      status: "ok",
      query,
      security: {
        symbol: row.symbol || null,
        issuer_name: row.issuer_name,
        cusip: row.cusip || null,
        sector: row.sector,
      },
      portfolio_position: {
        weight_label: row.weight_label,
        value_label: row.value_label,
        shares_label: "-",
      },
      charts: fallbackCharts || {
        daily: { label: "일봉", points: [] },
        weekly: { label: "주봉", points: [] },
        monthly: { label: "월봉", points: [] },
      },
      price_action: {
        action_id: "collect_price_history",
        label: hasFallbackChart ? "가격 데이터 새로고침" : "가격 데이터 수집",
        symbol: row.symbol || null,
        start_date: payload.hero.latest_report_period,
        available: Boolean(row.symbol),
        needs_collection: !hasFallbackChart,
        reason: hasFallbackChart ? "저장된 가격 DB 기준 차트가 표시 중입니다." : "저장된 가격 row가 없어 차트가 비어 있습니다.",
      },
      holders: payload.interest.holders,
      holder_count: payload.interest.holder_count,
      caveat: "현재 포트폴리오 payload 기준의 즉시 표시입니다. 서버 응답 후 가격 차트와 보유 기관 정보가 보강됩니다.",
    };
  }, [payload, localSelectedQuery]);

  if (!payload) {
    return <div className="ip-empty">Institutional portfolio payload is unavailable.</div>;
  }

  const sendEvent = (event: Record<string, unknown>) => {
    Streamlit.setComponentValue({ event: { ...event, nonce: `${Date.now()}-${Math.random()}` } });
    syncFrameHeightSoon();
  };

  const switchView = (view: ViewName) => {
    const position = hostScrollPosition();
    setActiveView(view);
    restoreHostScroll(position);
    syncFrameHeightSoon();
  };

  const handleDrilldown = (query: string) => {
    if (!query) {
      return;
    }
    const position = hostScrollPosition();
    setActionNotice(null);
    setLocalSelectedQuery(query);
    setPendingAction({ kind: "interest", query, label: `${query} 종목 상세 불러오는 중` });
    setActiveView("interest");
    sendEvent({ id: "drilldown", query });
    restoreHostScroll(position);
  };

  const handleManagerSelect = (item: ManagerItem) => {
    if (!item.cik || item.selected) {
      return;
    }
    const rail = managerRailRef.current;
    if (rail) {
      managerRailScrollRef.current = rail.scrollLeft;
    }
    setActionNotice(null);
    setLocalSelectedQuery("");
    setPendingAction({ kind: "manager", cik: item.cik, label: `${item.manager_name} 포트폴리오 불러오는 중` });
    sendEvent({ id: "select_manager", cik: item.cik });
  };

  const handlePopularityLoad = () => {
    setActionNotice(null);
    setPendingAction({ kind: "popularity", label: "기관 보유 랭킹 불러오는 중" });
    sendEvent({ id: "open_popularity" });
  };

  const handlePriceCollect = (action: PriceAction) => {
    const symbol = String(action.symbol || "").toUpperCase();
    if (!symbol || !action.available) {
      return;
    }
    setActionNotice(null);
    setPendingAction({ kind: "price", symbol, label: `${symbol} 가격 데이터 수집 중` });
    sendEvent({ id: "collect_price_history", symbol, start_date: action.start_date || payload.hero.latest_report_period });
  };

  const handleRefreshOpen = () => {
    setActionNotice(null);
    setPendingAction({ kind: "refresh", label: "13F 데이터 갱신 설정을 여는 중" });
    sendEvent({ id: "open_refresh" });
    window.setTimeout(() => setPendingAction((current) => (current?.kind === "refresh" ? null : current)), 900);
  };

  return (
    <main className="ip-workbench" data-schema-version={payload.schema_version} data-mode={payload.mode}>
      <section className="ip-hero">
        <div className="ip-hero__topline">
          <span className={`ip-state ${payload.data_state.is_preview ? "ip-state--preview" : ""}`}>{payload.data_state.label}</span>
          <span>{payload.hero.caveat}</span>
        </div>

        <div
          className="ip-manager-rail"
          role="tablist"
          aria-label="Institutional managers"
          ref={managerRailRef}
          onScroll={(event) => {
            managerRailScrollRef.current = event.currentTarget.scrollLeft;
          }}
        >
          {payload.manager_picker.items.map((item) => (
            <button
              key={item.cik || item.manager_name}
              type="button"
              className={`ip-manager-tab ${item.selected ? "ip-manager-tab--active" : ""} ${
                pendingAction?.kind === "manager" && pendingAction.cik === item.cik ? "ip-manager-tab--pending" : ""
              }`}
              data-cik={item.cik || ""}
              disabled={Boolean(pendingAction)}
              onClick={() => handleManagerSelect(item)}
            >
              <strong>{item.manager_name}</strong>
              <span>{item.watchlist_label ? `${item.watchlist_label} · ${item.latest_report_period}` : item.latest_report_period}</span>
            </button>
          ))}
        </div>

        {pendingAction ? (
          <div className="ip-loading-banner" role="status" aria-live="polite">
            <span className="ip-spinner" aria-hidden="true" />
            <strong>
              {pendingAction.kind === "manager"
                ? "포트폴리오 불러오는 중"
                : pendingAction.kind === "interest"
                  ? "종목 상세 불러오는 중"
                  : pendingAction.kind === "popularity"
                    ? "기관 보유 랭킹 불러오는 중"
                    : pendingAction.kind === "price"
                      ? "가격 데이터 수집 중"
                      : "갱신 설정 여는 중"}
            </strong>
            <em>{pendingAction.label}</em>
          </div>
        ) : null}

        <div className={`ip-freshness ${payload.freshness?.is_stale ? "ip-freshness--stale" : ""}`}>
          <button type="button" className="ip-freshness__action" onClick={handleRefreshOpen}>
            {payload.refresh_action?.label || "SEC 13F 데이터"}
          </button>
          <strong>{payload.freshness?.latest_report_period || "로컬 13F 데이터 없음"}</strong>
          <em>{payload.freshness?.last_collected_at ? `수집 시각 ${payload.freshness.last_collected_at}` : "갱신 설정 사용 가능"}</em>
        </div>

        <div className="ip-hero__grid">
          <div className="ip-hero__identity">
            <div className="ip-hero__kicker">Institutional Portfolios</div>
            <h2>{payload.hero.manager_name}</h2>
            <p>{payload.data_state.message}</p>
            <div className="ip-hero__facts">
              {payload.hero.facts.map((fact) => (
                <div className="ip-fact" key={`${fact.label}-${fact.value}`}>
                  <span>{fact.label}</span>
                  <strong>{fact.value}</strong>
                </div>
              ))}
            </div>
            {payload.hero.source_ref ? (
              <a className="ip-source-link" href={payload.hero.source_ref} target="_blank" rel="noreferrer">
                SEC 원문 열기
              </a>
            ) : null}
          </div>

          <div className="ip-allocation-panel">
            <div className="ip-section-head">
              <div>
                <h3>{payload.allocation.title}</h3>
                <p>{payload.allocation.subtitle}</p>
              </div>
              <strong>{payload.allocation.total_label}</strong>
            </div>
            <div className="ip-allocation-layout">
              <AllocationDonut segments={payload.allocation.segments} />
              <div className="ip-holding-list">
                {payload.allocation.top_holdings.slice(0, 6).map((holding) => (
                  <button type="button" key={`${holding.key}-${holding.label}`} className="ip-holding-row" onClick={() => handleDrilldown(holding.drilldown_query)}>
                    <span className="ip-dot" style={{ backgroundColor: holding.color }} />
                    <span>
                      <strong>{holding.label}</strong>
                      <small>{holding.issuer_name}</small>
                    </span>
                    <em>{holding.weight_label}</em>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      <nav className="ip-view-tabs" aria-label="Institutional portfolio views">
        <button className={activeView === "overview" ? "ip-view-tabs__active" : ""} type="button" onClick={() => switchView("overview")}>
          요약
        </button>
        <button className={activeView === "holdings" ? "ip-view-tabs__active" : ""} type="button" onClick={() => switchView("holdings")}>
          전체 보유
        </button>
        <button className={activeView === "interest" ? "ip-view-tabs__active" : ""} type="button" onClick={() => switchView("interest")}>
          보유 기관 조회
        </button>
        <button className={activeView === "popularity" ? "ip-view-tabs__active" : ""} type="button" onClick={() => switchView("popularity")}>
          기관 보유 랭킹
        </button>
      </nav>

      <div className="ip-view-body">
        {activeView === "overview" ? (
          <section className="ip-grid">
            <div className="ip-stack">
              <PortfolioPerformancePanel performance={payload.portfolio_performance} onDrilldown={handleDrilldown} />
              <div className="ip-panel ip-panel--changes">
                <div className="ip-section-head">
                  <div>
                    <h3>{payload.change_board.title}</h3>
                    <p>{payload.change_board.subtitle}</p>
                  </div>
                </div>
                {!payload.change_board.comparison_available ? <div className="ip-board-note">{payload.change_board.empty_reason}</div> : null}
                <div className="ip-change-grid">
                  {changeGroups.map((group) => (
                    <div className="ip-change-card" key={group.key}>
                      <div className="ip-change-card__head">
                        <span>{group.label}</span>
                        <strong>{group.count}</strong>
                      </div>
                      <p>{group.description}</p>
                      <div className="ip-change-card__items">
                        {group.items.length ? (
                          group.items.map((item) => (
                            <button type="button" key={`${group.key}-${item.label}`} onClick={() => handleDrilldown(item.drilldown_query)}>
                              <span>{item.label}</span>
                              <em>{item.value_delta_label}</em>
                            </button>
                          ))
                        ) : (
                          <small>표시할 row 없음</small>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="ip-panel">
              <div className="ip-section-head">
                <div>
                  <h3>{payload.sector_exposure.title}</h3>
                  <p>{payload.sector_exposure.subtitle}</p>
                </div>
              </div>
              <div className="ip-sector-bars">
                {payload.sector_exposure.bars.map((bar) => (
                  <div className="ip-sector-row" key={bar.sector}>
                    <div>
                      <strong>{bar.sector}</strong>
                      <span>{bar.holding_count}개 종목 · {bar.value_label}</span>
                    </div>
                    <div className="ip-sector-row__track">
                      <span style={{ width: `${clampPercent(bar.bar_width_pct)}%`, backgroundColor: bar.color }} />
                    </div>
                    <em>{bar.weight_label}</em>
                  </div>
                ))}
              </div>
            </div>
          </section>
        ) : null}

        {activeView === "holdings" ? (
          <section className="ip-panel">
            <div className="ip-section-head">
              <div>
                <h3>전체 보유 종목</h3>
                <p>종목을 클릭하면 아래의 보유 기관 조회 화면에서 종목 상세와 기관 리스트를 함께 보여줍니다.</p>
              </div>
              <strong>{payload.holdings_table.rows.length}</strong>
            </div>
            <div className="ip-table">
              {payload.holdings_table.rows.slice(0, 80).map((row) => (
                <button type="button" key={`${row.cusip}-${row.issuer_name}`} onClick={() => handleDrilldown(row.drilldown_query)}>
                  <span>{row.symbol || "-"}</span>
                  <strong>{row.issuer_name}</strong>
                  <em>{row.weight_label}</em>
                  <small>{row.value_label}</small>
                  <small>{row.sector}</small>
                </button>
              ))}
            </div>
          </section>
        ) : null}

        {activeView === "interest" ? (
          <section className="ip-panel">
            <div className="ip-section-head">
              <div>
                <h3>보유 기관 조회</h3>
                <p>
                  {payload.interest.query || localSelectedQuery
                    ? `${payload.interest.query || localSelectedQuery} 종목 상세와 보유 기관`
                    : payload.interest.empty_text}
                </p>
              </div>
              <strong>{payload.interest.holder_count}</strong>
            </div>
            <SecurityDetail
              detail={localSecurityDetail}
              interest={{ ...payload.interest, query: payload.interest.query || localSelectedQuery }}
              notice={actionNotice}
              priceRefresh={payload.price_refresh_result}
              disabled={Boolean(pendingAction)}
              onCollectPrice={handlePriceCollect}
            />
          </section>
        ) : null}

        {activeView === "popularity" ? (
          <PopularityRankingPanel popularity={payload.popularity} onLoad={handlePopularityLoad} onDrilldown={handleDrilldown} />
        ) : null}
      </div>

      {payload.source_caveats.visible ? (
        <section className="ip-caveats">
          {payload.source_caveats.items.slice(0, 5).map((item) => (
            <span key={item}>{item}</span>
          ))}
        </section>
      ) : null}
    </main>
  );
}

export default withStreamlitConnection(InstitutionalPortfoliosWorkbench);
