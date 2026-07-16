import React from "react"
import { CharacterProfileItem, ReviewPressureItem } from "./decisionBriefTypes"

const PRESSURE_LABELS: Record<ReviewPressureItem["status"], string> = {
  within_limit: "기준 이내",
  exceeds_limit: "기준 초과",
  criterion_missing: "기준 미설정",
  evidence_missing: "분석 근거 없음",
}

export function DecisionBriefCharacter({
  characterItems,
  pressureItems,
}: {
  characterItems: CharacterProfileItem[]
  pressureItems: ReviewPressureItem[]
}) {
  return (
    <div className="db-character-layout">
      <section className="db-character-panel" aria-labelledby="db-character-profile-title">
        <div className="db-character-panel-heading">
          <p className="db-kicker">Observed character</p>
          <h3 id="db-character-profile-title">포트폴리오 실제 성격</h3>
          <p>저장된 관측값을 기준 유무와 관계없이 먼저 읽습니다.</p>
        </div>
        <div className="db-character-list">
          {characterItems.map((item) => (
            <article key={item.axis_id} className={`db-character-card is-${item.measurement_status}`}>
              <span>{item.label}</span>
              <strong>{item.display_value}</strong>
              <p>{item.interpretation}</p>
              <small>{item.as_of ? `기준일 ${item.as_of}` : "저장된 기준일 없음"}</small>
            </article>
          ))}
        </div>
      </section>
      <section className="db-pressure-panel" aria-labelledby="db-review-pressure-title">
        <div className="db-character-panel-heading">
          <p className="db-kicker">Review pressure</p>
          <h3 id="db-review-pressure-title">관리 기준 대비 압력</h3>
          <p>점수가 아니라 저장된 review criterion과의 차이입니다.</p>
        </div>
        <div className="db-pressure-list">
          {pressureItems.map((item) => (
            <article key={item.axis_id} className={`db-pressure-row is-${item.status}`}>
              <div>
                <span>{item.label}</span>
                <strong>{PRESSURE_LABELS[item.status]}</strong>
              </div>
              <p>{item.summary}</p>
              {item.criterion_display && (
                <small>관측 {item.display_value} · 기준 {item.criterion_display}</small>
              )}
            </article>
          ))}
        </div>
      </section>
    </div>
  )
}
