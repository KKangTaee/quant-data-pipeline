import React, { useEffect, useMemo, useState } from "react";
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
  weight_label: string;
  value_label: string;
  source_ref?: string | null;
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
    groups: Record<string, ChangeGroup>;
  };
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

function syncFrameHeightSoon() {
  Streamlit.setFrameHeight();
  window.requestAnimationFrame(() => Streamlit.setFrameHeight());
  window.setTimeout(() => Streamlit.setFrameHeight(), 180);
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
          return (
            <path
              key={segment.key}
              d={arcPath(start, end, 72)}
              stroke={segment.color}
              className="ip-donut__arc"
            />
          );
        })}
      </svg>
      <div className="ip-donut__center">
        <strong>{segments[0]?.weight_label || "0.0%"}</strong>
        <span>{segments[0]?.label || "No holdings"}</span>
      </div>
    </div>
  );
}

function InstitutionalPortfoliosWorkbench({ args }: Props) {
  const payload = args.payload;
  const [activeView, setActiveView] = useState<"overview" | "holdings" | "interest">("overview");

  useEffect(() => {
    Streamlit.setComponentReady();
    syncFrameHeightSoon();
  }, []);

  useEffect(() => {
    syncFrameHeightSoon();
  }, [payload, activeView]);

  const changeGroups = useMemo(() => {
    if (!payload) {
      return [];
    }
    return ["reported_new", "increased", "reduced", "no_longer_reported"].map((key) => ({
      key,
      ...payload.change_board.groups[key],
    }));
  }, [payload]);

  if (!payload) {
    return <div className="ip-empty">Institutional portfolio payload is unavailable.</div>;
  }

  const sendEvent = (event: Record<string, unknown>) => {
    Streamlit.setComponentValue(event);
    syncFrameHeightSoon();
  };

  const handleDrilldown = (query: string) => {
    if (!query) {
      return;
    }
    setActiveView("interest");
    sendEvent({ event: "drilldown", query });
  };

  return (
    <main className="ip-workbench" data-schema-version={payload.schema_version} data-mode={payload.mode}>
      <section className="ip-hero">
        <div className="ip-hero__topline">
          <span className={`ip-state ${payload.data_state.is_preview ? "ip-state--preview" : ""}`}>
            {payload.data_state.label}
          </span>
          <span>{payload.hero.caveat}</span>
        </div>

        <div className="ip-manager-rail" role="tablist" aria-label="Institutional managers">
          {payload.manager_picker.items.map((item) => (
            <button
              key={item.cik || item.manager_name}
              type="button"
              className={`ip-manager-tab ${item.selected ? "ip-manager-tab--active" : ""}`}
              onClick={() => item.cik && sendEvent({ event: "select_manager", cik: item.cik })}
            >
              <strong>{item.manager_name}</strong>
              <span>{item.watchlist_label ? `${item.watchlist_label} · ${item.latest_report_period}` : item.latest_report_period}</span>
            </button>
          ))}
        </div>

        <div className={`ip-freshness ${payload.freshness?.is_stale ? "ip-freshness--stale" : ""}`}>
          <span>{payload.refresh_action?.label || "SEC 13F data"}</span>
          <strong>{payload.freshness?.latest_report_period || "No local 13F data"}</strong>
          <em>{payload.freshness?.last_collected_at ? `collected ${payload.freshness.last_collected_at}` : "refresh available below"}</em>
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
                Open source filing
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
                  <button
                    type="button"
                    key={`${holding.key}-${holding.label}`}
                    className="ip-holding-row"
                    onClick={() => handleDrilldown(holding.drilldown_query)}
                  >
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
        <button className={activeView === "overview" ? "ip-view-tabs__active" : ""} type="button" onClick={() => setActiveView("overview")}>
          Overview
        </button>
        <button className={activeView === "holdings" ? "ip-view-tabs__active" : ""} type="button" onClick={() => setActiveView("holdings")}>
          Holdings
        </button>
        <button className={activeView === "interest" ? "ip-view-tabs__active" : ""} type="button" onClick={() => setActiveView("interest")}>
          Institutional Interest
        </button>
      </nav>

      {activeView === "overview" ? (
        <section className="ip-grid">
          <div className="ip-panel ip-panel--changes">
            <div className="ip-section-head">
              <div>
                <h3>{payload.change_board.title}</h3>
                <p>{payload.change_board.subtitle}</p>
              </div>
            </div>
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
                      <small>No rows</small>
                    )}
                  </div>
                </div>
              ))}
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
                    <span>{bar.holding_count} holdings · {bar.value_label}</span>
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
              <h3>Full Holdings</h3>
              <p>Click a holding to see latest stored 13F holders for that security.</p>
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
              <h3>Institutional Interest</h3>
              <p>{payload.interest.query ? `Latest stored 13F holders for ${payload.interest.query}` : payload.interest.empty_text}</p>
            </div>
            <strong>{payload.interest.holder_count}</strong>
          </div>
          <div className="ip-interest-list">
            {payload.interest.holders.length ? (
              payload.interest.holders.map((holder) => (
                <a href={holder.source_ref || "#"} target="_blank" rel="noreferrer" key={`${holder.cik}-${holder.manager_name}`}>
                  <span>
                    <strong>{holder.manager_name}</strong>
                    <small>{holder.period_of_report} · filed {holder.filing_date}</small>
                  </span>
                  <em>{holder.weight_label}</em>
                  <small>{holder.value_label}</small>
                </a>
              ))
            ) : (
              <div className="ip-interest-empty">{payload.interest.empty_text}</div>
            )}
          </div>
        </section>
      ) : null}

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
