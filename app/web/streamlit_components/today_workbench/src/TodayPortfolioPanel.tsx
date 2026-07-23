import { memo } from "react";

import TodayPortfolioChart from "./TodayPortfolioChart";
import { displayPortfolio, signedMoneyText } from "./presentation";
import type { TodayPortfolio } from "./types";

type Props = {
  portfolio: TodayPortfolio;
  viewportWidth: number;
};

function moneyText(value: number | null) {
  if (value == null || !Number.isFinite(value)) return "—";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);
}

function percentText(value: number | null) {
  if (value == null || !Number.isFinite(value)) return "—";
  return `${value > 0 ? "+" : ""}${(value * 100).toFixed(2)}%`;
}

function shortDate(value: string | null) {
  if (!value) return "-";
  const parts = value.slice(0, 10).split("-");
  return parts.length === 3 ? `${parts[1]}.${parts[2]}` : value;
}

const TodayPortfolioPanel = memo(function TodayPortfolioPanel({
  portfolio,
  viewportWidth,
}: Props) {
  const display = displayPortfolio(portfolio);
  const recentTone = (display.latestObservationReturn ?? 0) < 0 ? "is-negative" : "is-positive";
  const totalTone = (display.totalReturn ?? 0) < 0 ? "is-negative" : "is-positive";

  return (
    <section className="today-portfolio-panel">
      <header className="today-portfolio-heading">
        <div>
          <span className="today-eyebrow">REPRESENTATIVE PORTFOLIO</span>
          <h2>{portfolio.name}</h2>
          <p>{portfolio.summary} · 기준 {portfolio.basis_date ?? "-"}</p>
        </div>
        <b className={`today-portfolio-status status-${portfolio.status.toLowerCase()}`}>
          {portfolio.status === "READY" ? "정상 추적" : "확인 필요"}
        </b>
      </header>
      <div className="today-metrics" aria-live="polite">
        <article>
          <span>현재 평가액</span>
          <strong>{moneyText(display.currentValue)}</strong>
          <small>
            {display.badge}
            {display.asOfUtc
              ? ` · ${new Intl.DateTimeFormat("en-GB", {
                timeZone: "America/New_York",
                hour: "2-digit",
                minute: "2-digit",
                hourCycle: "h23",
              }).format(new Date(display.asOfUtc))} ET`
              : ` · ${portfolio.basis_date ?? "-"}`}
          </small>
        </article>
        <article>
          <span>{display.latestReturnLabel}</span>
          <strong className={recentTone}>{percentText(display.latestObservationReturn)}</strong>
          <small>{shortDate(display.returnFromDate)} → {shortDate(display.returnToDate)}</small>
        </article>
        <article>
          <span>누적 수익률</span>
          <strong className={totalTone}>{percentText(display.totalReturn)}</strong>
          <small>{display.coverageText ?? "현금흐름 조정"}</small>
        </article>
      </div>
      <TodayPortfolioChart
        rows={portfolio.curve}
        metadata={portfolio.curve_metadata}
        livePoint={display.livePoint}
        viewportWidth={viewportWidth}
      />
      <div className="today-portfolio-detail-grid">
        <section className="today-contributor-section">
          <header className="today-detail-heading">
            <span>종목별 성과 기여</span>
            <small>기여 상위 2 · 하위 2</small>
          </header>
          <div className="today-contributor-grid">
            {display.contributors.length
              ? display.contributors.map((row) => {
                const returnTone = row.total_return == null
                  ? "is-unavailable"
                  : row.total_return < 0 ? "is-negative" : "is-positive";
                const contributionTone = row.tone === "negative"
                  ? "is-negative"
                  : "is-positive";
                return (
                  <article
                    className="today-contributor-card"
                    key={`${row.symbol}-${row.contribution_value}`}
                  >
                    <strong className="today-contributor-symbol">{row.symbol}</strong>
                    <span className="today-contributor-return-label">종목 누적 수익률</span>
                    <b className={`today-contributor-return ${returnTone}`}>
                      {row.total_return == null
                        ? "수익률 자료 부족"
                        : percentText(row.total_return)}
                    </b>
                    <footer>
                      <span>포트폴리오 누적 기여</span>
                      <strong className={contributionTone}>
                        {signedMoneyText(row.contribution_value)}
                      </strong>
                    </footer>
                  </article>
                );
              })
              : <small>기여 계산 자료가 없습니다.</small>}
          </div>
          <small className="today-contributor-note">
            종목 수익률은 입출금 영향을 조정한 누적 성과 · {display.badge}
          </small>
        </section>
        <section>
          <span>우선 확인</span>
          <div className="today-review-list">
            {portfolio.review_items.length
              ? portfolio.review_items.map((row) => (
                <p key={`${row.severity}-${row.meaning}`}>
                  <b>{row.severity}</b>{row.meaning}
                </p>
              ))
              : <small>현재 우선 확인 항목이 없습니다.</small>}
          </div>
        </section>
      </div>
    </section>
  );
});

export default TodayPortfolioPanel;
