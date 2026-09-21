import React from "react";
import { ConditionEvidence, Reading } from "./contracts";
import { change, kst, priceClass } from "./presentation";

function Pair({ evidence }: { evidence: ConditionEvidence[] }) {
  return (
    <div className="pair">
      {evidence.map((e) => (
        <div key={e.symbol}>
          <span>{e.label}</span>
          <b className={priceClass(e.return_pct)}>
            {change(e.return_pct)} <small>{e.direction}</small>
          </b>
        </div>
      ))}
    </div>
  );
}
export default function ObservationReading({
  reading: r,
}: {
  reading: Reading;
}) {
  return (
    <section className="reading">
      <div className="section-heading">
        <h3>두 가지 확인 결과</h3>
        <span className="muted">같은 구간의 실제 가격으로 판정</span>
      </div>
      <div className="checks">
        {r.condition_results.map((c, i) => (
          <article className={`check tone-${c.tone}`} key={c.key}>
            <div className="check-title">
              <span className="number">0{i + 1}</span>
              <h4>{c.title}</h4>
            </div>
            <Pair evidence={c.evidence} />
            <div className="conclusion">
              <span className="conclusion-label">확인 결과</span>
              <h4>{c.verdict}</h4>
              <p>{c.explanation}</p>
            </div>
            <div className="comparison">
              <span
                className={`comparison-label ${c.comparison.status.toLowerCase()}`}
              >
                {c.comparison.status === "CHANGED"
                  ? "1시간 전과 달라짐"
                  : c.comparison.status === "UNCHANGED"
                    ? "1시간 전에도 같은 조합"
                    : "이전 관측 비교 불가"}
              </span>
              <p>{c.comparison.summary}</p>
              {c.comparison.previous_evidence && (
                <details>
                  <summary>1시간 전 판정에 사용한 값</summary>
                  <p className="muted">
                    {kst(c.comparison.previous_start_utc || null)} →{" "}
                    {kst(c.comparison.previous_end_utc || null)} KST
                  </p>
                  <Pair evidence={c.comparison.previous_evidence} />
                </details>
              )}
            </div>
          </article>
        ))}
      </div>
      {r.counter_evidence.map((f) => (
        <p className="counter" key={f}>
          <b>함께 읽을 점</b> {f}
        </p>
      ))}
      <p className="reading-note">
        상승·하락은 0.01% 표시 단위의 방향이며 영향의 크기를 뜻하지 않습니다.
        <br />
        현재와 1시간 전의 관측을 비교한 해석입니다. 다음 시간의 방향을 예측한
        결과는 아닙니다.
      </p>
    </section>
  );
}
