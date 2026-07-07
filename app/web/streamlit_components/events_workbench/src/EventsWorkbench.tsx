import React, { useEffect } from "react";
import { Streamlit, withStreamlitConnection, ComponentProps } from "streamlit-component-lib";
import "./style.css";

type EventBadge = {
  label: string;
  kind: string;
};

type EventItem = {
  date: string;
  days_until?: number | null;
  type: string;
  family: string;
  symbol?: string;
  title: string;
  importance?: string;
  validation?: string;
  freshness?: string;
  source_authority?: string;
  universe_scope?: string;
  needs_review?: boolean;
  badges?: EventBadge[];
};

type EventRail = {
  key: string;
  label: string;
  count: number;
  review_count: number;
  items: EventItem[];
};

type EventsPayload = {
  schema_version?: string;
  status?: string;
  brief?: {
    title?: string;
    boundary_note?: string;
    next_event?: EventItem | null;
    counts?: Record<string, number>;
    source_summary?: Record<string, number>;
    freshness_summary?: {
      latest_collected_at?: string | null;
      stale_estimate_count?: number;
      has_stale_estimates?: boolean;
      warning_count?: number;
    };
    family_counts?: Record<string, number>;
  };
  rails?: EventRail[];
  trust_review?: {
    title?: string;
    official_count?: number;
    provider_estimate_count?: number;
    not_confirmed_count?: number;
    stale_estimate_count?: number;
    warnings?: string[];
  };
};

function valueText(value: unknown, fallback = "-"): string {
  if (value === null || value === undefined || value === "") {
    return fallback;
  }
  return String(value);
}

function CountTile({ label, value }: { label: string; value: unknown }) {
  return (
    <div className="events-workbench__count-tile">
      <span>{label}</span>
      <strong>{valueText(value, "0")}</strong>
    </div>
  );
}

function EventCard({ item }: { item: EventItem }) {
  const title = item.symbol ? `${item.symbol} · ${item.title}` : item.title;
  return (
    <article className="events-workbench__event-card">
      <div className="events-workbench__event-date">{item.date}</div>
      <div className="events-workbench__event-title">{title}</div>
      <div className="events-workbench__event-meta">
        {valueText(item.type)} · {valueText(item.freshness)} · {valueText(item.validation)}
      </div>
      <div className="events-workbench__badges">
        {(item.badges || []).slice(0, 4).map((badge) => (
          <span className={`events-workbench__badge events-workbench__badge--${badge.kind}`} key={`${badge.kind}-${badge.label}`}>
            {badge.label}
          </span>
        ))}
      </div>
    </article>
  );
}

function EventsWorkbench({ args }: ComponentProps) {
  const payload = ((args || {}).payload || {}) as EventsPayload;
  payload.rails = payload.rails || [];
  const brief = payload.brief || {};
  const counts = brief.counts || {};
  const sourceSummary = brief.source_summary || {};
  const freshness = brief.freshness_summary || {};
  const trust = payload.trust_review || {};
  const isPayloadReady = payload.schema_version === "events_workbench_v1";

  useEffect(() => {
    Streamlit.setFrameHeight();
  }, [payload]);

  const emitEvent = (id: string) => {
    Streamlit.setComponentValue({ event: { id } });
  };

  if (!isPayloadReady) {
    return (
      <section className="events-workbench">
        <div className="events-workbench__fallback-note">Events workbench payload unavailable.</div>
      </section>
    );
  }

  return (
    <section className="events-workbench">
      <header className="events-workbench__hero">
        <div className="events-workbench__hero-copy">
          <span className="events-workbench__eyebrow">Events</span>
          <h2>{brief.title || "다가오는 시장 이벤트 브리프"}</h2>
          <p>{brief.boundary_note}</p>
        </div>
        <div className="events-workbench__next-card">
          <span className="events-workbench__eyebrow">Next</span>
          <strong>{brief.next_event ? brief.next_event.date : "No event"}</strong>
          <p>{brief.next_event ? brief.next_event.title : "No upcoming event in the current window."}</p>
        </div>
      </header>

      <div className="events-workbench__counts">
        <CountTile label="Today" value={counts.today} />
        <CountTile label="This Week" value={counts.this_week} />
        <CountTile label="Next 30D" value={counts.next_30d} />
        <CountTile label="Official" value={sourceSummary.official} />
        <CountTile label="Estimates" value={sourceSummary.provider_estimate} />
        <CountTile label="Stale" value={freshness.stale_estimate_count} />
      </div>

      <div className="events-workbench__rails">
        {payload.rails.map((rail) => (
          <section className="events-workbench__rail" key={rail.key}>
            <div className="events-workbench__rail-header">
              <h3>{rail.label}</h3>
              <span>{rail.count} rows · {rail.review_count} review</span>
            </div>
            <div className="events-workbench__rail-items">
              {rail.items.slice(0, 4).map((item) => (
                <EventCard item={item} key={`${rail.key}-${item.date}-${item.type}-${item.symbol || item.title}`} />
              ))}
              {!rail.items.length && <div className="events-workbench__empty">No rows</div>}
            </div>
          </section>
        ))}
      </div>

      <section className="events-workbench__trust">
        <div>
          <span className="events-workbench__eyebrow">Trust</span>
          <h3>{trust.title || "자료 신뢰 / 추정 일정 확인"}</h3>
        </div>
        <div className="events-workbench__trust-grid">
          <CountTile label="Official" value={trust.official_count} />
          <CountTile label="Provider Estimate" value={trust.provider_estimate_count} />
          <CountTile label="Not Confirmed" value={trust.not_confirmed_count} />
          <CountTile label="Stale Estimate" value={trust.stale_estimate_count} />
        </div>
      </section>

      <button className="events-workbench__hidden-action" type="button" onClick={() => emitEvent("noop")}>
        Component ready
      </button>
    </section>
  );
}

export default withStreamlitConnection(EventsWorkbench);
