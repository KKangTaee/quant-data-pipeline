import React from "react";
import { WindowData } from "./contracts";
import { change, kst, priceClass } from "./presentation";

export default function AssetChangeStrip({
  window: w,
}: {
  window: WindowData;
}) {
  const t = w.time_context;
  return (
    <section className="prices">
      <div className="section-heading">
        <h3>선물 가격 변화</h3>
        <span className="basis-tag">{t.label}</span>
      </div>
      <div className="time-band">
        <div>
          <span>비교 시작</span>
          <b>{kst(w.start_utc)}</b>
        </div>
        <span className="time-arrow" aria-hidden="true">
          →
        </span>
        <div>
          <span>마지막 관측</span>
          <b>{kst(w.end_utc)}</b>
        </div>
        <span className="time-zone">한국시간 KST</span>
      </div>
      <p className="time-note">
        화면 조회 {kst(t.evaluated_at_utc)} KST 기준
        {t.observation_age_minutes !== null &&
          ` · 마지막 관측은 조회 시점보다 ${t.observation_age_minutes}분 전`}
        <br />위 두 시점 사이의 변화율입니다. 실시간 현재가 등락률이 아닙니다.
      </p>
      <div className="price-grid">
        {w.prices.map((p) => (
          <div className="price" key={p.key}>
            <span className="price-name">{p.label}</span>
            <strong className={priceClass(p.return_pct)}>
              {change(p.return_pct)}
            </strong>
            <small>
              {p.return_pct === null
                ? "같은 구간의 비교 자료 부족"
                : p.description}
            </small>
          </div>
        ))}
      </div>
    </section>
  );
}
