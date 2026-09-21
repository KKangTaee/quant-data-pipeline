import React from "react";
import {WindowData} from "./contracts";
import {kst,statusLabels} from "./presentation";
export default function IntradayChangeSummary({window:w}:{window:WindowData}) {
 return <section className="story"><div className="eyebrow">이번 구간에서 달라진 것 <span className={`status ${w.status.toLowerCase()}`}>{statusLabels[w.status]}</span></div>
 <h2>{w.reading.headline}</h2><p className="muted">{kst(w.start_utc)} → {kst(w.end_utc)} KST · 같은 시각의 완료 5분봉 비교</p></section>;
}
