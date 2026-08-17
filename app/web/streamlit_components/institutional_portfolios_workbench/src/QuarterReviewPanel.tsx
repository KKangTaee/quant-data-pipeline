import React, { useEffect, useMemo, useState } from "react";
import { filterQuarterReviewRows } from "./workbenchState";

type ProxyRow = {
  cusip: string;
  holding_symbol?: string | null;
  issuer_name?: string | null;
  weight_pct: number;
  return_pct: number;
  contribution_pct: number;
};

type PriceProxy = {
  proxy_id: string;
  status: "READY" | "LIMITED" | "NOT_AVAILABLE" | string;
  start_date: string;
  end_date: string;
  coverage_weight_pct: number;
  missing_weight_pct: number;
  covered_sleeve_return_pct?: number | null;
  rows: ProxyRow[];
  top_contributors?: ProxyRow[];
  top_detractors?: ProxyRow[];
};

export type QuarterReviewChange = {
  cusip: string;
  issuer_name?: string | null;
  holding_symbol?: string | null;
  change_type: "NEW" | "ADD" | "KEEP" | "REDUCE" | "DROP" | "NOT_COMPARABLE" | string;
  previous_amount?: number | null;
  current_amount?: number | null;
  previous_weight_pct: number;
  current_weight_pct: number;
  symbol_return_pct?: number | null;
  contribution_pct?: number | null;
};

export type QuarterReviewPayload = {
  available: boolean;
  manager?: { cik?: string; manager_name?: string };
  reason?: string;
  transition?: {
    previous_report_period?: string;
    current_report_period?: string;
    previous_filing_date?: string;
    current_filing_date?: string;
  };
  change_summary?: Record<string, number>;
  changes?: QuarterReviewChange[];
  proxies?: {
    quarter_holdings_proxy?: PriceProxy;
    public_follow_proxy?: PriceProxy;
  };
  caveat?: string;
  transitions?: QuarterReviewPayload[];
};

const CHANGE_TYPES = ["NEW", "ADD", "KEEP", "REDUCE", "DROP", "NOT_COMPARABLE"];

function numberLabel(value: number | null | undefined, digits = 2) {
  if (value === null || value === undefined || !Number.isFinite(Number(value))) {
    return "-";
  }
  return Number(value).toLocaleString(undefined, { maximumFractionDigits: digits });
}

function percentLabel(value: number | null | undefined) {
  if (value === null || value === undefined || !Number.isFinite(Number(value))) {
    return "-";
  }
  const numeric = Number(value);
  return `${numeric > 0 ? "+" : ""}${numeric.toFixed(2)}%`;
}

function ProxyCard({ title, subtitle, proxy }: { title: string; subtitle: string; proxy?: PriceProxy }) {
  if (!proxy) {
    return <div className="ip-review-proxy ip-review-proxy--empty">성과 근거가 없습니다.</div>;
  }
  return (
    <article className={`ip-review-proxy is-${proxy.status.toLowerCase()}`}>
      <div className="ip-review-proxy__head">
        <div><span>{subtitle}</span><h3>{title}</h3></div>
        <strong>{proxy.status}</strong>
      </div>
      <div className="ip-review-proxy__return">
        <strong>{percentLabel(proxy.covered_sleeve_return_pct)}</strong>
        <span>커버된 보유분 수익</span>
      </div>
      <dl>
        <div><dt>기간</dt><dd>{proxy.start_date} → {proxy.end_date}</dd></div>
        <div><dt>가격 커버리지</dt><dd>{numberLabel(proxy.coverage_weight_pct)}%</dd></div>
        <div><dt>미반영 비중</dt><dd>{numberLabel(proxy.missing_weight_pct)}%</dd></div>
      </dl>
    </article>
  );
}

function ContributionList({ title, rows }: { title: string; rows: ProxyRow[] }) {
  return (
    <div className="ip-review-contribution-list">
      <h4>{title}</h4>
      {rows.length ? rows.map((row) => (
        <div key={`${title}-${row.cusip}`}>
          <span><strong>{row.holding_symbol || row.cusip}</strong><small>{row.issuer_name}</small></span>
          <em>{percentLabel(row.contribution_pct)}</em>
        </div>
      )) : <p>표시할 가격 기여 근거가 없습니다.</p>}
    </div>
  );
}

export function QuarterReviewPanel({ review: suppliedReview }: { review?: QuarterReviewPayload }) {
  const transitionReviews = suppliedReview?.transitions?.length
    ? suppliedReview.transitions
    : suppliedReview ? [suppliedReview] : [];
  const [transitionIndex, setTransitionIndex] = useState(0);
  useEffect(() => {
    setTransitionIndex(0);
  }, [suppliedReview?.manager?.cik, suppliedReview?.transition?.current_report_period]);
  const safeTransitionIndex = Math.min(transitionIndex, Math.max(0, transitionReviews.length - 1));
  const review = transitionReviews[safeTransitionIndex] || suppliedReview;
  const [changeType, setChangeType] = useState("all");
  const [query, setQuery] = useState("");
  const changes = review?.changes || [];
  const filteredChanges = useMemo(
    () => filterQuarterReviewRows(changes, { changeType, query }),
    [changes, changeType, query]
  );
  if (!review?.available) {
    return (
      <section className="ip-panel ip-quarter-review-empty">
        <span>분기 비교 준비 중</span>
        <h3>한 분기의 공시가 더 필요합니다</h3>
        <p>{review?.reason || "비교할 이전 보고 분기가 저장되어 있지 않습니다."}</p>
      </section>
    );
  }

  const quarterProxy = review.proxies?.quarter_holdings_proxy;
  const publicProxy = review.proxies?.public_follow_proxy;
  return (
    <section className="ip-quarter-review">
      <div className="ip-panel ip-review-transition">
        <div>
          <span>보고 포트폴리오 전환</span>
          <h2>{review.transition?.previous_report_period} → {review.transition?.current_report_period}</h2>
          {transitionReviews.length > 1 ? (
            <label className="ip-review-transition-selector">
              <span>분기 전환 선택</span>
              <select
                value={safeTransitionIndex}
                onChange={(event) => {
                  setTransitionIndex(Number(event.target.value));
                  setChangeType("all");
                  setQuery("");
                }}
              >
                {transitionReviews.map((item, index) => (
                  <option key={`${item.transition?.previous_report_period}-${item.transition?.current_report_period}`} value={index}>
                    {item.transition?.previous_report_period} → {item.transition?.current_report_period}
                  </option>
                ))}
              </select>
            </label>
          ) : null}
        </div>
        <dl>
          <div><dt>이전 제출</dt><dd>{review.transition?.previous_filing_date || "-"}</dd></div>
          <div><dt>현재 제출</dt><dd>{review.transition?.current_filing_date || "-"}</dd></div>
        </dl>
      </div>

      <div className="ip-review-proxy-grid">
        <ProxyCard title="분기 보유 결과" subtitle="보고 기준일 → 다음 보고 기준일" proxy={quarterProxy} />
        <ProxyCard title="공개 후 추종 결과" subtitle="제출일 → 다음 제출일" proxy={publicProxy} />
      </div>

      <div className="ip-panel ip-review-change-panel">
        <div className="ip-section-head">
          <div><h3>포지션 변화</h3><p>평가액이 아니라 보고 수량·원금 기준으로 분류합니다.</p></div>
          <strong>{filteredChanges.length.toLocaleString()} / {changes.length.toLocaleString()}</strong>
        </div>
        <div className="ip-review-change-filters">
          <button type="button" className={changeType === "all" ? "is-active" : ""} onClick={() => setChangeType("all")}>전체 {changes.length}</button>
          {CHANGE_TYPES.map((type) => (
            <button key={type} type="button" className={changeType === type ? "is-active" : ""} onClick={() => setChangeType(type)}>
              {type} {Number(review.change_summary?.[type] || 0)}
            </button>
          ))}
          <input type="search" value={query} placeholder="ticker, 발행사, CUSIP" onChange={(event) => setQuery(event.target.value)} />
        </div>
        <div className="ip-review-table-wrap">
          <table className="ip-review-table">
            <thead><tr><th>변화</th><th>종목</th><th>이전 수량</th><th>현재 수량</th><th>이전 비중</th><th>현재 비중</th><th>분기 수익</th><th>기여도</th></tr></thead>
            <tbody>
              {filteredChanges.map((row) => (
                <tr key={`${row.cusip}-${row.change_type}`}>
                  <td><span className={`ip-review-change-badge is-${row.change_type.toLowerCase()}`}>{row.change_type}</span></td>
                  <td><strong>{row.holding_symbol || row.cusip}</strong><small>{row.issuer_name}</small></td>
                  <td>{numberLabel(row.previous_amount)}</td><td>{numberLabel(row.current_amount)}</td>
                  <td>{numberLabel(row.previous_weight_pct)}%</td><td>{numberLabel(row.current_weight_pct)}%</td>
                  <td>{percentLabel(row.symbol_return_pct)}</td><td>{percentLabel(row.contribution_pct)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {!filteredChanges.length ? <div className="ip-interest-empty">조건에 맞는 변화가 없습니다.</div> : null}
        </div>
      </div>

      <div className="ip-panel ip-review-contributions">
        <ContributionList title="기여 상위" rows={quarterProxy?.top_contributors || []} />
        <ContributionList title="기여 하위" rows={quarterProxy?.top_detractors || []} />
      </div>
      <p className="ip-note">{review.caveat}</p>
    </section>
  );
}
