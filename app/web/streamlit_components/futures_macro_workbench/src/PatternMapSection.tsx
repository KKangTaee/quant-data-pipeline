import { useState } from "react";
import type { HorizonCard, PatternMapPayload, PatternPoint, ProbabilityRow, RegimeKey } from "./FuturesMacroWorkbench";

const WIDTH = 720;
const HEIGHT = 390;
const PAD_X = 64;
const PAD_Y = 34;

type SelectedHorizon = "observed" | "5D" | "20D";
type AnchorPoint = PatternPoint & { anchorLabel: string };

const REGIME_TARGETS: Record<RegimeKey, { x: number; y: number }> = {
  risk_seeking: { x: 0.74, y: -0.48 },
  defensive: { x: -0.74, y: 0.48 },
  inflation_rate_pressure: { x: 0.28, y: 0.78 },
  mixed: { x: 0.06, y: 0.04 },
};

function pointAt(path: PatternPoint[], daysAgo: number): PatternPoint | undefined {
  if (path.length <= daysAgo) return undefined;
  return path[path.length - 1 - daysAgo];
}

function observedAnchors(path: PatternPoint[]): AnchorPoint[] {
  const candidates = [
    { point: pointAt(path, 20), anchorLabel: "20D 전" },
    { point: pointAt(path, 5), anchorLabel: "5D 전" },
    { point: pointAt(path, 0), anchorLabel: "현재" },
  ];
  const seen = new Set<string>();
  return candidates.flatMap(({ point, anchorLabel }) => {
    if (!point || seen.has(point.date)) return [];
    seen.add(point.date);
    return [{ ...point, anchorLabel }];
  });
}

function Branch({
  row,
  latest,
  sx,
  sy,
  xBound,
  yBound,
}: {
  row: ProbabilityRow;
  latest: PatternPoint;
  sx: (value: number) => number;
  sy: (value: number) => number;
  xBound: number;
  yBound: number;
}) {
  const target = REGIME_TARGETS[row.key];
  const targetX = target.x * xBound;
  const targetY = target.y * yBound;
  const startX = sx(latest.x);
  const startY = sy(latest.y);
  const endX = sx(targetX);
  const endY = sy(targetY);
  const controlX = startX + (endX - startX) * 0.52;
  const controlY = startY + (endY - startY) * 0.34;
  const probability = Math.max(0, Math.min(1, row.value));
  const percentage = Math.round(row.value * 100);

  return (
    <g className={`fm-pattern-map__outcome regime-${row.key}`}>
      <path
        className="fm-pattern-map__branch"
        d={`M ${startX} ${startY} Q ${controlX} ${controlY} ${endX} ${endY}`}
        style={{ opacity: Math.min(1, 0.38 + probability * 1.05), strokeWidth: 1.25 + probability * 5 }}
      >
        <title>{row.label} 조건부 분기 · {percentage}%</title>
      </path>
      <circle className="fm-pattern-map__outcome-dot" cx={endX} cy={endY} r={8 + probability * 16} />
      <text className="fm-pattern-map__outcome-value" x={endX} y={endY + 4} textAnchor="middle">{percentage}</text>
      <text className="fm-pattern-map__outcome-label" x={endX} y={endY + 34} textAnchor="middle">{row.label}</text>
    </g>
  );
}

function PatternMapSection({ patternMap, horizons }: { patternMap: PatternMapPayload; horizons: HorizonCard[] }) {
  const [selectedHorizon, setSelectedHorizon] = useState<SelectedHorizon>("5D");
  const anchors = observedAnchors(patternMap.path);
  const latest = anchors.at(-1);
  const selectedCard = horizons.find((item) => item.key === selectedHorizon);
  const probabilities = selectedCard?.kind === "conditional_outlook" ? selectedCard.probabilities || [] : [];
  const xBound = Math.max(1.25, ...anchors.map((point) => Math.abs(point.x) * 1.18));
  const yBound = Math.max(1.1, ...anchors.map((point) => Math.abs(point.y) * 1.18));
  const sx = (value: number) => PAD_X + ((value + xBound) / (xBound * 2)) * (WIDTH - PAD_X * 2);
  const sy = (value: number) => HEIGHT - PAD_Y - ((value + yBound) / (yBound * 2)) * (HEIGHT - PAD_Y * 2);
  const observedPoints = anchors.map((point) => `${sx(point.x)},${sy(point.y)}`).join(" ");
  const showForecast = selectedHorizon !== "observed" && Boolean(latest) && probabilities.length > 0;

  return (
    <section className="fm-workbench__pattern-map" aria-labelledby="fm-pattern-map-title">
      <div className="fm-workbench__section-heading fm-pattern-map__heading">
        <div><span>Observed + conditional outlook</span><h3 id="fm-pattern-map-title">최근 시장 위치와 조건부 다음 경로</h3></div>
        <div className="fm-pattern-map__controls" aria-label="전망 기간 선택">
          <button type="button" data-horizon="observed" aria-pressed={selectedHorizon === "observed"} onClick={() => setSelectedHorizon("observed")}>관측만</button>
          <button type="button" data-horizon="5D" aria-pressed={selectedHorizon === "5D"} onClick={() => setSelectedHorizon("5D")}>다음 5D</button>
          <button type="button" data-horizon="20D" aria-pressed={selectedHorizon === "20D"} onClick={() => setSelectedHorizon("20D")}>다음 20D</button>
        </div>
      </div>

      <div className="fm-pattern-map__body">
        <div className="fm-pattern-map__canvas">
          <svg role="img" viewBox={`0 0 ${WIDTH} ${HEIGHT}`} aria-label="세 관측 시점과 선택한 기간의 조건부 체제 분기">
            <defs>
              <marker id="fm-observed-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" />
              </marker>
            </defs>
            <rect className="fm-pattern-map__quadrant quadrant-defense" x={PAD_X} y={PAD_Y} width={WIDTH / 2 - PAD_X} height={HEIGHT / 2 - PAD_Y} />
            <rect className="fm-pattern-map__quadrant quadrant-pressure" x={WIDTH / 2} y={PAD_Y} width={WIDTH / 2 - PAD_X} height={HEIGHT / 2 - PAD_Y} />
            <rect className="fm-pattern-map__quadrant quadrant-calm" x={PAD_X} y={HEIGHT / 2} width={WIDTH / 2 - PAD_X} height={HEIGHT / 2 - PAD_Y} />
            <rect className="fm-pattern-map__quadrant quadrant-risk" x={WIDTH / 2} y={HEIGHT / 2} width={WIDTH / 2 - PAD_X} height={HEIGHT / 2 - PAD_Y} />
            <line className="fm-pattern-map__axis" x1={sx(0)} x2={sx(0)} y1={PAD_Y} y2={HEIGHT - PAD_Y} />
            <line className="fm-pattern-map__axis" x1={PAD_X} x2={WIDTH - PAD_X} y1={sy(0)} y2={sy(0)} />
            <text className="fm-pattern-map__quadrant-label" x={PAD_X + 18} y={PAD_Y + 24}>방어 · 부담 강화</text>
            <text className="fm-pattern-map__quadrant-label" x={WIDTH - PAD_X - 18} y={PAD_Y + 24} textAnchor="end">위험선호 · 부담 강화</text>
            <text className="fm-pattern-map__quadrant-label" x={PAD_X + 18} y={HEIGHT - PAD_Y - 18}>방어 · 부담 완화</text>
            <text className="fm-pattern-map__quadrant-label" x={WIDTH - PAD_X - 18} y={HEIGHT - PAD_Y - 18} textAnchor="end">위험선호 · 부담 완화</text>

            {showForecast ? probabilities.map((row) => (
              <Branch key={`${selectedHorizon}-${row.key}`} row={row} latest={latest!} sx={sx} sy={sy} xBound={xBound} yBound={yBound} />
            )) : null}
            {observedPoints ? <polyline className="fm-pattern-map__observed" markerEnd="url(#fm-observed-arrow)" points={observedPoints} /> : null}
            {anchors.map((point, index) => (
              <g className={`fm-pattern-map__anchor ${point.anchorLabel === "현재" ? "is-current" : ""}`} key={`${point.date}-${point.anchorLabel}`}>
                <circle cx={sx(point.x)} cy={sy(point.y)} r={point.anchorLabel === "현재" ? 10 : 7} />
                <text x={sx(point.x)} y={sy(point.y) - (index === 1 ? 16 : 14)} textAnchor="middle">{point.anchorLabel === "현재" ? `현재 · ${point.regime_label}` : point.anchorLabel}</text>
                <title>{point.anchorLabel} · {point.date} · {point.regime_label} · {point.transition_label}</title>
              </g>
            ))}
          </svg>
          <span className="fm-pattern-map__x-label">{patternMap.x_label} 강화 →</span>
          <span className="fm-pattern-map__y-label">{patternMap.y_label} 강화 →</span>
        </div>

        <aside className="fm-pattern-map__reading" aria-live="polite">
          {selectedHorizon === "observed" ? (
            <>
              <span>현재 관측</span>
              <strong>20D 전 → 5D 전 → 현재의 실제 이동</strong>
              <dl>
                {anchors.map((point) => <div key={`reading-${point.date}`}><dt>{point.anchorLabel}</dt><dd>{point.regime_label}</dd></div>)}
              </dl>
              <p>실선과 핵심 시점만 표시하며 미래 확률은 포함하지 않습니다.</p>
            </>
          ) : (
            <>
              <div className="fm-pattern-map__reading-head">
                <span>다음 {selectedHorizon} · 조건부 전망</span>
                <b className={`estimate-${(selectedCard?.estimate_status || "UNAVAILABLE").toLowerCase()}`}>{selectedCard?.estimate_status || "UNAVAILABLE"}</b>
              </div>
              <strong>{selectedCard?.edge_label || "방향 우위 미확인"}</strong>
              {probabilities.length > 0 ? (
                <dl>
                  {probabilities.map((row) => <div key={`probability-${row.key}`}><dt>{row.label}</dt><dd>{Math.round(row.value * 100)}%</dd></div>)}
                </dl>
              ) : <div className="fm-pattern-map__unavailable">확률을 표시할 근거가 부족합니다.</div>}
              <p>{selectedCard?.episode_count ? `독립 표본 ${selectedCard.episode_count}개 · ` : ""}점선은 가능한 체제 분기이며 실제 이동 경로가 아닙니다.</p>
              {selectedCard?.status_reason ? <small>{selectedCard.status_reason}</small> : null}
            </>
          )}
        </aside>
      </div>

      <div className="fm-pattern-map__legend">
        <span className="observed">관측 경로</span>
        <span className="forecast">조건부 분기</span>
        <span className="current">현재 위치</span>
        <small>원 안의 숫자 = 해당 체제 확률(%)</small>
      </div>
    </section>
  );
}

export default PatternMapSection;
