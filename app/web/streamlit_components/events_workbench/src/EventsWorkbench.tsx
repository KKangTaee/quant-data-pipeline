import React, { useEffect, useState } from "react";
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
  source_type?: string;
  source_url?: string;
  confidence?: unknown;
  collected_at?: string;
  event_time?: string;
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

type EventAction = {
  id: string;
  label: string;
  kind?: string;
  detail?: string;
};

type TrustSection = {
  key: string;
  label: string;
  count: number;
  items: EventItem[];
};

type TrustReview = {
  title?: string;
  official_count?: number;
  provider_estimate_count?: number;
  estimate_only_count?: number;
  cross_checked_count?: number;
  not_confirmed_count?: number;
  stale_estimate_count?: number;
  conflict_count?: number;
  warnings?: string[];
  sections?: TrustSection[];
  source_boundary?: string;
};

type CalendarDay = {
  date: string;
  count: number;
  review_count: number;
  stale_count: number;
  by_family?: Record<string, number>;
  top_titles?: string[];
  items?: EventItem[];
};

type DensityBucket = {
  week_start: string;
  count: number;
  review_count: number;
  stale_count: number;
  by_family?: Record<string, number>;
};

type EvidencePayload = {
  raw_fields?: string[];
  rows?: Record<string, unknown>[];
  row_count?: number;
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
  trust_review?: TrustReview;
  command?: {
    title?: string;
    refresh_boundary?: string;
    actions?: EventAction[];
  };
  calendar?: {
    days?: CalendarDay[];
    density?: DensityBucket[];
  };
  evidence?: EvidencePayload;
};

const FAMILY_OPTIONS = [
  { id: "all", label: "All" },
  { id: "central_bank", label: "FOMC" },
  { id: "macro", label: "Macro" },
  { id: "earnings", label: "Earnings" },
  { id: "market_structure", label: "Market Structure" },
];

const REVIEW_OPTIONS = [
  { id: "all", label: "All" },
  { id: "review", label: "Review" },
  { id: "official", label: "Official" },
  { id: "estimate", label: "Estimate" },
];

function valueText(value: unknown, fallback = "-"): string {
  if (value === null || value === undefined || value === "") {
    return fallback;
  }
  return String(value);
}

function normalizedText(value: unknown): string {
  return valueText(value, "").trim().toLowerCase();
}

function cssToken(value: unknown): string {
  return normalizedText(value).replace(/[^a-z0-9_-]+/g, "_") || "unknown";
}

function familyLabel(value: unknown): string {
  const family = normalizedText(value);
  if (family === "central_bank") {
    return "FOMC";
  }
  if (family === "market_structure") {
    return "Market Structure";
  }
  if (family === "fixed_income") {
    return "Fixed Income";
  }
  return valueText(value, "Unknown").replace(/_/g, " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function familyTone(value: unknown): string {
  const family = normalizedText(value);
  if (family === "central_bank") {
    return "fomc";
  }
  if (family === "market_structure") {
    return "structure";
  }
  if (family === "fixed_income") {
    return "macro";
  }
  return cssToken(family);
}

function matchesFamily(item: EventItem, familyFilter: string): boolean {
  if (familyFilter === "all") {
    return true;
  }
  const family = normalizedText(item.family);
  const type = normalizedText(item.type);
  if (familyFilter === "central_bank") {
    return family === "central_bank" || type.includes("fomc");
  }
  if (familyFilter === "macro") {
    return family === "macro" || family === "fixed_income" || type.startsWith("macro") || type.startsWith("treasury");
  }
  return family === familyFilter;
}

function matchesReviewState(item: EventItem, reviewFilter: string): boolean {
  if (reviewFilter === "all") {
    return true;
  }
  const authority = normalizedText(item.source_authority);
  const validation = normalizedText(item.validation);
  if (reviewFilter === "review") {
    return Boolean(item.needs_review);
  }
  if (reviewFilter === "official") {
    return ["official", "issuer_confirmed", "cross_checked"].includes(authority) || validation === "official";
  }
  if (reviewFilter === "estimate") {
    return (
      authority.includes("estimate") ||
      authority.includes("not_confirmed") ||
      ["estimate only", "not confirmed", "conflict"].includes(validation)
    );
  }
  return true;
}

function filterItems(items: EventItem[], familyFilter: string, reviewFilter: string): EventItem[] {
  return items.filter((item) => matchesFamily(item, familyFilter) && matchesReviewState(item, reviewFilter));
}

function aggregateFamilies(items: EventItem[]): Record<string, number> {
  return items.reduce<Record<string, number>>((acc, item) => {
    const family = item.family || "unknown";
    acc[family] = (acc[family] || 0) + 1;
    return acc;
  }, {});
}

function weekMatchesFilter(bucket: DensityBucket, familyFilter: string, reviewFilter: string): boolean {
  if (reviewFilter === "review" && !bucket.review_count) {
    return false;
  }
  if (reviewFilter === "estimate" && !bucket.review_count && !bucket.stale_count) {
    return false;
  }
  if (familyFilter === "all") {
    return true;
  }
  const families = bucket.by_family || {};
  if (familyFilter === "macro") {
    return Boolean(families.macro || families.fixed_income);
  }
  return Boolean(families[familyFilter]);
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
    <article className={`events-workbench__event-card events-workbench__event-card--${familyTone(item.family)}`}>
      <div className="events-workbench__event-date">
        {item.date}
        {item.event_time && item.event_time !== "-" ? <span>{item.event_time}</span> : null}
      </div>
      <div className="events-workbench__event-title">{title}</div>
      <div className="events-workbench__event-meta">
        {valueText(item.type)} · {valueText(item.freshness)} · {valueText(item.validation)}
      </div>
      <div className="events-workbench__badges">
        {(item.badges || []).slice(0, 5).map((badge) => (
          <span className={`events-workbench__badge events-workbench__badge--${badge.kind}`} key={`${badge.kind}-${badge.label}`}>
            {badge.label}
          </span>
        ))}
      </div>
    </article>
  );
}

function TrustItem({ item }: { item: EventItem }) {
  const title = item.symbol ? `${item.symbol} · ${item.title}` : item.title;
  return (
    <div className="events-workbench__trust-item">
      <strong>{title}</strong>
      <span>
        {item.date} · {valueText(item.source_authority)} · {valueText(item.freshness)}
      </span>
    </div>
  );
}

function dayTooltipText(day: CalendarDay): string {
  const titles = (day.top_titles || []).slice(0, 3).join(" / ");
  return `${day.date} · ${day.count} events · ${day.review_count} review · ${day.stale_count} stale${titles ? ` · ${titles}` : ""}`;
}

function rawValue(row: Record<string, unknown>, key: string): string {
  return valueText(row[key]);
}

function EventsWorkbench({ args }: ComponentProps) {
  const payload = ((args || {}).payload || {}) as EventsPayload;
  const rails = payload.rails || [];
  const command = payload.command || { actions: [] };
  const commandActions = command.actions || [];
  const calendar = payload.calendar || { days: [], density: [] };
  const calendarDays = calendar.days || [];
  const calendarDensity = calendar.density || [];
  const evidence = payload.evidence || { rows: [] };
  const evidenceRows = evidence.rows || [];
  const brief = payload.brief || {};
  const counts = brief.counts || {};
  const sourceSummary = brief.source_summary || {};
  const freshness = brief.freshness_summary || {};
  const trust = payload.trust_review || {};
  const trustSections = trust.sections || [];
  const [pendingActionId, setPendingActionId] = useState("");
  const [familyFilter, setFamilyFilter] = useState("all");
  const [reviewFilter, setReviewFilter] = useState("all");
  const [expandedEvidence, setExpandedEvidence] = useState(false);
  const isPayloadReady = payload.schema_version === "events_workbench_v1";

  const familyOptions = FAMILY_OPTIONS;
  const reviewOptions = REVIEW_OPTIONS;
  const filteredRails = rails.map((rail) => {
    const items = filterItems(rail.items || [], familyFilter, reviewFilter);
    return {
      ...rail,
      count: items.length,
      review_count: items.filter((item) => item.needs_review).length,
      items,
    };
  });
  const filteredCalendarDays = calendarDays
    .map((day) => {
      const items = filterItems(day.items || [], familyFilter, reviewFilter);
      return {
        ...day,
        count: items.length,
        review_count: items.filter((item) => item.needs_review).length,
        stale_count: items.filter((item) => normalizedText(item.freshness).includes("stale")).length,
        by_family: aggregateFamilies(items),
        top_titles: items.slice(0, 3).map((item) => item.title),
        items,
      };
    })
    .filter((day) => day.count > 0);
  const filteredDensity = calendarDensity.filter((bucket) => weekMatchesFilter(bucket, familyFilter, reviewFilter));
  const maxDensityCount = Math.max(1, ...filteredDensity.map((bucket) => bucket.count || 0));

  useEffect(() => {
    Streamlit.setFrameHeight();
  }, [payload]);

  useEffect(() => {
    Streamlit.setFrameHeight();
  }, [familyFilter, reviewFilter, expandedEvidence, pendingActionId]);

  useEffect(() => {
    setPendingActionId("");
  }, [payload.schema_version, brief.freshness_summary?.latest_collected_at]);

  const emitEvent = (id: string) => {
    setPendingActionId(id);
    Streamlit.setComponentValue({ event: { id, nonce: `${Date.now()}-${Math.random()}` } });
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

      <section className="events-workbench__command">
        <div className="events-workbench__command-copy">
          <span className="events-workbench__eyebrow">Refresh</span>
          <h3>{command.title || "화면 / 수집 갱신"}</h3>
          <p>{command.refresh_boundary}</p>
        </div>
        <div className="events-workbench__actions">
          {commandActions.map((action) => (
            <button
              className={`events-workbench__action events-workbench__action--${action.kind || "secondary"}`}
              disabled={pendingActionId === action.id}
              key={action.id}
              onClick={() => emitEvent(action.id)}
              title={action.detail || action.label}
              type="button"
            >
              {pendingActionId === action.id ? "실행 중" : action.label}
            </button>
          ))}
        </div>
      </section>

      <section className="events-workbench__filterbar">
        <div className="events-workbench__filtergroup">
          <span>Type</span>
          <div>
            {familyOptions.map((option) => (
              <button
                className={familyFilter === option.id ? "events-workbench__filter is-active" : "events-workbench__filter"}
                key={option.id}
                onClick={() => setFamilyFilter(option.id)}
                type="button"
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>
        <div className="events-workbench__filtergroup">
          <span>Source State</span>
          <div>
            {reviewOptions.map((option) => (
              <button
                className={reviewFilter === option.id ? "events-workbench__filter is-active" : "events-workbench__filter"}
                key={option.id}
                onClick={() => setReviewFilter(option.id)}
                type="button"
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>
      </section>

      <div className="events-workbench__rails">
        {filteredRails.map((rail) => (
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
          {trust.source_boundary ? <p>{trust.source_boundary}</p> : null}
        </div>
        <div>
          <div className="events-workbench__trust-grid">
            <CountTile label="Official" value={trust.official_count} />
            <CountTile label="Provider Estimate" value={trust.provider_estimate_count} />
            <CountTile label="Not Confirmed" value={trust.not_confirmed_count} />
            <CountTile label="Stale Estimate" value={trust.stale_estimate_count} />
          </div>
          <div className="events-workbench__trust-sections">
            {trustSections.map((section) => {
              const items = filterItems(section.items || [], familyFilter, reviewFilter);
              return (
                <section className="events-workbench__trust-section" key={section.key}>
                  <div className="events-workbench__trust-section-head">
                    <strong>{section.label}</strong>
                    <span>{items.length}</span>
                  </div>
                  {items.slice(0, 3).map((item) => (
                    <TrustItem item={item} key={`${section.key}-${item.date}-${item.type}-${item.symbol || item.title}`} />
                  ))}
                  {!items.length && <div className="events-workbench__empty events-workbench__empty--compact">No rows</div>}
                </section>
              );
            })}
          </div>
          {(trust.warnings || []).length ? (
            <div className="events-workbench__warnings">
              {(trust.warnings || []).slice(0, 3).map((warning) => (
                <span key={warning}>{warning}</span>
              ))}
            </div>
          ) : null}
        </div>
      </section>

      <section className="events-workbench__calendar">
        <div className="events-workbench__section-head">
          <div>
            <span className="events-workbench__eyebrow">Calendar</span>
            <h3>그래프로 보는 일정 근거</h3>
          </div>
          <span>{filteredCalendarDays.length} active dates</span>
        </div>
        <div className="events-workbench__calendar-grid">
          {filteredCalendarDays.slice(0, 35).map((day) => (
            <div className="events-workbench__day" key={day.date} title={dayTooltipText(day)}>
              <div className="events-workbench__day-head">
                <strong>{day.date.slice(5)}</strong>
                <span>{day.count}</span>
              </div>
              <div className="events-workbench__day-families">
                {Object.entries(day.by_family || {}).map(([family, count]) => (
                  <span className={`events-workbench__family-dot events-workbench__family-dot--${familyTone(family)}`} key={family}>
                    {familyLabel(family)} {count}
                  </span>
                ))}
              </div>
              <div className="events-workbench__day-meta">
                {day.review_count} review · {day.stale_count} stale
              </div>
              <div className="events-workbench__day-tooltip" role="tooltip">
                <strong>{day.date}</strong>
                <span>{day.count} events · {day.review_count} review · {day.stale_count} stale</span>
                {(day.top_titles || []).slice(0, 3).map((title) => (
                  <em key={`${day.date}-${title}`}>{title}</em>
                ))}
              </div>
            </div>
          ))}
          {!filteredCalendarDays.length && <div className="events-workbench__empty">No dated rows</div>}
        </div>

        <div className="events-workbench__density">
          {filteredDensity.slice(0, 12).map((bucket) => (
            <div className="events-workbench__density-row" key={bucket.week_start}>
              <span>{bucket.week_start}</span>
              <div className="events-workbench__density-bar" title={`${bucket.count} events · ${bucket.review_count} review`}>
                <div className="events-workbench__density-fill" style={{ width: `${Math.max(8, (bucket.count / maxDensityCount) * 100)}%` }}>
                  {Object.entries(bucket.by_family || {}).map(([family, count]) => (
                    <i
                      className={`events-workbench__density-segment events-workbench__density-segment--${familyTone(family)}`}
                      key={`${bucket.week_start}-${family}`}
                      style={{ width: `${Math.max(8, (Number(count) / Math.max(1, bucket.count)) * 100)}%` }}
                    />
                  ))}
                </div>
              </div>
              <strong>{bucket.count}</strong>
            </div>
          ))}
        </div>
      </section>

      <section className="events-workbench__evidence">
        <div className="events-workbench__section-head">
          <div>
            <span className="events-workbench__eyebrow">Evidence</span>
            <h3>원본 / 상세 근거</h3>
          </div>
          <button type="button" onClick={() => setExpandedEvidence(!expandedEvidence)}>
            {expandedEvidence ? "접기" : `${valueText(evidence.row_count, "0")} rows`}
          </button>
        </div>
        {expandedEvidence ? (
          <div className="events-workbench__evidence-table">
            <div className="events-workbench__evidence-head">
              <span>Date</span>
              <span>Type</span>
              <span>Title</span>
              <span>Source</span>
              <span>Collected</span>
            </div>
            {evidenceRows.slice(0, 10).map((row, index) => (
              <div className="events-workbench__evidence-row" key={`${rawValue(row, "Date")}-${rawValue(row, "Type")}-${index}`}>
                <span>{rawValue(row, "Date")}</span>
                <span>{rawValue(row, "Type")}</span>
                <strong>{rawValue(row, "Symbol") !== "-" ? `${rawValue(row, "Symbol")} · ${rawValue(row, "Title")}` : rawValue(row, "Title")}</strong>
                <span>
                  {rawValue(row, "Source URL").startsWith("http") ? (
                    <a href={rawValue(row, "Source URL")} rel="noreferrer" target="_blank">
                      {rawValue(row, "Source Authority")}
                    </a>
                  ) : (
                    rawValue(row, "Source Authority")
                  )}
                </span>
                <span>{rawValue(row, "Collected At")}</span>
              </div>
            ))}
          </div>
        ) : null}
      </section>

      <button className="events-workbench__hidden-action" type="button" onClick={() => emitEvent("noop")}>
        Component ready
      </button>
    </section>
  );
}

export default withStreamlitConnection(EventsWorkbench);
