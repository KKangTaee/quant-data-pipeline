import { useState } from "react";
import type { HorizonCard, PatternMapPayload, PatternPoint } from "./FuturesMacroWorkbench";

const WIDTH = 720;
const HEIGHT = 390;
const PAD_X = 64;
const PAD_Y = 34;

type SelectedHorizon = "observed" | "5D" | "20D";
type AnchorPoint = PatternPoint & { anchorLabel: string };
type ScreenPoint = { x: number; y: number };
type ScreenSegment = { x1: number; y1: number; x2: number; y2: number };

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

/** Places a compact arrow segment between endpoints so its marker cannot cover either point. */
function directionSegment(
  start: ScreenPoint | undefined,
  end: ScreenPoint | undefined,
  { startInset, endInset, length }: { startInset: number; endInset: number; length: number },
): ScreenSegment | undefined {
  if (!start || !end) return undefined;
  const dx = end.x - start.x;
  const dy = end.y - start.y;
  const distance = Math.hypot(dx, dy);
  const available = distance - startInset - endInset;
  if (!Number.isFinite(distance) || distance <= 0 || available <= 4) return undefined;
  const unitX = dx / distance;
  const unitY = dy / distance;
  const segmentLength = Math.min(length, available);
  const centerDistance = startInset + available * 0.55;
  const firstDistance = centerDistance - segmentLength / 2;
  const secondDistance = centerDistance + segmentLength / 2;
  return {
    x1: start.x + unitX * firstDistance,
    y1: start.y + unitY * firstDistance,
    x2: start.x + unitX * secondDistance,
    y2: start.y + unitY * secondDistance,
  };
}

function PatternMapSection({ patternMap, horizons }: { patternMap: PatternMapPayload; horizons: HorizonCard[] }) {
  const [selectedHorizon, setSelectedHorizon] = useState<SelectedHorizon>("5D");
  const anchors = observedAnchors(patternMap.path);
  const latest = anchors.at(-1);
  const selectedCard = horizons.find((item) => item.key === selectedHorizon);
  const probabilities = selectedCard?.kind === "conditional_outlook" ? selectedCard.probabilities || [] : [];
  const conditionalPath = selectedCard?.kind === "conditional_outlook" ? selectedCard?.conditional_path : undefined;
  const forecastPoints = conditionalPath?.status !== "UNAVAILABLE" ? conditionalPath?.points || [] : [];
  const scalePaths = horizons.flatMap((item) => (
    item.kind === "conditional_outlook"
      && item.conditional_path
      && item.conditional_path.status !== "UNAVAILABLE"
      ? [item.conditional_path]
      : []
  ));
  const scaleTerminalPoints = scalePaths.flatMap((path) => (
    path.terminal ? [path.terminal] : []
  ));
  const xValues = [
    ...anchors.map((point) => point.x),
    ...scaleTerminalPoints.flatMap((point) => [point.x, point.lower_x, point.upper_x]),
  ];
  const yValues = [
    ...anchors.map((point) => point.y),
    ...scaleTerminalPoints.flatMap((point) => [point.y, point.lower_y, point.upper_y]),
  ];
  const xBound = Math.max(1.25, ...xValues.map((value) => Math.abs(value) * 1.12));
  const yBound = Math.max(1.1, ...yValues.map((value) => Math.abs(value) * 1.12));
  const sx = (value: number) => PAD_X + ((value + xBound) / (xBound * 2)) * (WIDTH - PAD_X * 2);
  const sy = (value: number) => HEIGHT - PAD_Y - ((value + yBound) / (yBound * 2)) * (HEIGHT - PAD_Y * 2);
  const observedPoints = anchors.map((point) => `${sx(point.x)},${sy(point.y)}`).join(" ");
  const uncertaintyStep = forecastPoints.at(-1);
  const selectedDays = selectedHorizon === "observed"
    ? undefined
    : Number.parseInt(selectedHorizon, 10);
  const expectedPositionLabel = selectedDays ? `${selectedDays}일 후 예상 위치` : "";
  const forecastLegend = selectedDays ? `${selectedDays}일 예상 순이동` : "예상 순이동";
  const rangeLegend = selectedDays ? `${selectedDays}일 후 도착 범위` : "도착 범위";
  const showForecast = selectedHorizon !== "observed" && Boolean(latest) && forecastPoints.length > 0;
  const pathStatus = conditionalPath?.status || "UNAVAILABLE";
  const terminal = conditionalPath?.terminal || undefined;
  const screenPoint = (point: { x: number; y: number } | undefined): ScreenPoint | undefined => (
    point ? { x: sx(point.x), y: sy(point.y) } : undefined
  );
  const observedDirection = directionSegment(
    screenPoint(anchors.at(-2)),
    screenPoint(latest),
    { startInset: 10, endInset: 14, length: 18 },
  );
  const forecastDirection = directionSegment(
    screenPoint(latest),
    screenPoint(terminal),
    { startInset: 13, endInset: 11, length: 12 },
  );

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
          <svg role="img" viewBox={`0 0 ${WIDTH} ${HEIGHT}`} aria-label="세 관측 시점과 선택한 기간의 과거 유사 흐름 기반 예상 이동">
            <defs>
              <marker id="fm-observed-direction-arrow" markerUnits="userSpaceOnUse" viewBox="0 0 9 9" refX="8" refY="4.5" markerWidth="9" markerHeight="9" orient="auto">
                <path d="M 0 0 L 9 4.5 L 0 9 z" />
              </marker>
              <marker id="fm-forecast-direction-arrow" markerUnits="userSpaceOnUse" viewBox="0 0 9 9" refX="8" refY="4.5" markerWidth="9" markerHeight="9" orient="auto">
                <path d="M 0 0 L 9 4.5 L 0 9 z" />
              </marker>
            </defs>
            <rect className="fm-pattern-map__quadrant quadrant-defense" x={PAD_X} y={PAD_Y} width={WIDTH / 2 - PAD_X} height={HEIGHT / 2 - PAD_Y} />
            <rect className="fm-pattern-map__quadrant quadrant-pressure" x={WIDTH / 2} y={PAD_Y} width={WIDTH / 2 - PAD_X} height={HEIGHT / 2 - PAD_Y} />
            <rect className="fm-pattern-map__quadrant quadrant-calm" x={PAD_X} y={HEIGHT / 2} width={WIDTH / 2 - PAD_X} height={HEIGHT / 2 - PAD_Y} />
            <rect className="fm-pattern-map__quadrant quadrant-risk" x={WIDTH / 2} y={HEIGHT / 2} width={WIDTH / 2 - PAD_X} height={HEIGHT / 2 - PAD_Y} />
            <line className="fm-pattern-map__axis" x1={sx(0)} x2={sx(0)} y1={PAD_Y} y2={HEIGHT - PAD_Y} />
            <line className="fm-pattern-map__axis" x1={PAD_X} x2={WIDTH - PAD_X} y1={sy(0)} y2={sy(0)} />
            <text className="fm-pattern-map__quadrant-label" x={PAD_X + 18} y={PAD_Y + 24}>방어 · 금리·달러·물가 압력 강화</text>
            <text className="fm-pattern-map__quadrant-label" x={WIDTH - PAD_X - 18} y={PAD_Y + 24} textAnchor="end">위험선호 · 금리·달러·물가 압력 강화</text>
            <text className="fm-pattern-map__quadrant-label" x={PAD_X + 18} y={HEIGHT - PAD_Y - 18}>방어 · 금리·달러·물가 압력 완화</text>
            <text className="fm-pattern-map__quadrant-label" x={WIDTH - PAD_X - 18} y={HEIGHT - PAD_Y - 18} textAnchor="end">위험선호 · 금리·달러·물가 압력 완화</text>

            {showForecast && uncertaintyStep ? (
              <rect
                className="fm-pattern-map__uncertainty"
                data-forecast-step={uncertaintyStep.step}
                x={sx(uncertaintyStep.lower_x)}
                y={sy(uncertaintyStep.upper_y)}
                width={Math.max(2, sx(uncertaintyStep.upper_x) - sx(uncertaintyStep.lower_x))}
                height={Math.max(2, sy(uncertaintyStep.lower_y) - sy(uncertaintyStep.upper_y))}
                rx="10"
              >
                <title>{selectedDays}일 후 · {conditionalPath?.band_label}</title>
              </rect>
            ) : null}
            {showForecast && latest && terminal ? (
              <line
                className="fm-pattern-map__conditional-path"
                data-forecast-horizon={selectedHorizon}
                x1={sx(latest.x)}
                y1={sy(latest.y)}
                x2={sx(terminal.x)}
                y2={sy(terminal.y)}
              />
            ) : null}
            {observedPoints ? <polyline className="fm-pattern-map__observed" points={observedPoints} /> : null}
            {observedDirection ? (
              <line
                className="fm-pattern-map__direction is-observed"
                data-direction="observed"
                {...observedDirection}
                markerEnd="url(#fm-observed-direction-arrow)"
              />
            ) : null}
            {showForecast && forecastDirection ? (
              <line
                className="fm-pattern-map__direction is-forecast"
                data-direction="forecast"
                {...forecastDirection}
                markerEnd="url(#fm-forecast-direction-arrow)"
              />
            ) : null}
            {anchors.map((point) => (
              <g className={`fm-pattern-map__anchor ${point.anchorLabel === "현재" ? "is-current" : ""}`} key={`${point.date}-${point.anchorLabel}`}>
                <circle cx={sx(point.x)} cy={sy(point.y)} r={point.anchorLabel === "현재" ? 10 : 7.5} />
                {point.anchorLabel === "현재" ? (
                  <>
                    <line className="fm-pattern-map__leader" x1={sx(point.x) - 7} y1={sy(point.y) + 7} x2={sx(point.x) - 35} y2={sy(point.y) + 30} />
                    <text x={sx(point.x) - 40} y={sy(point.y) + 36} textAnchor="end">현재</text>
                  </>
                ) : (
                  <text x={sx(point.x)} y={sy(point.y) - 14} textAnchor="middle">{point.anchorLabel}</text>
                )}
                <title>{point.anchorLabel} · {point.date} · {point.regime_label} · {point.transition_label}</title>
              </g>
            ))}
            {showForecast && terminal ? (
              <g className="fm-pattern-map__terminal">
                <circle cx={sx(terminal.x)} cy={sy(terminal.y)} r="8" />
                <line className="fm-pattern-map__leader" x1={sx(terminal.x) + 6} y1={sy(terminal.y) - 6} x2={sx(terminal.x) + 40} y2={sy(terminal.y) - 36} />
                <text className="fm-pattern-map__terminal-label" x={sx(terminal.x) + 46} y={sy(terminal.y) - 40} textAnchor="start">{expectedPositionLabel}</text>
                <title>다음 {selectedHorizon} · 독립 표본 {conditionalPath?.episode_count}개 · {pathStatus}</title>
              </g>
            ) : null}
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
                <b className={`estimate-${pathStatus.toLowerCase()}`}>{pathStatus}</b>
              </div>
              <strong>{selectedCard?.edge_label || "방향 우위 미확인"}</strong>
              {probabilities.length > 0 ? (
                <dl>
                  {probabilities.map((row) => <div key={`probability-${row.key}`}><dt>{row.label}</dt><dd>{Math.round(row.value * 100)}%</dd></div>)}
                </dl>
              ) : <div className="fm-pattern-map__unavailable">확률을 표시할 근거가 부족합니다.</div>}
              {!showForecast ? <div className="fm-pattern-map__unavailable">조건부 경로를 표시할 독립 표본 또는 검증 근거가 부족합니다.</div> : null}
              <p>{conditionalPath?.episode_count ? `독립 표본 ${conditionalPath.episode_count}개 · ` : ""}점선은 과거 유사 흐름의 시작점에서 말일 중앙 위치까지의 예상 순이동이며, 중간 일별 경로가 아닙니다. 실제 미래 경로를 보장하지 않습니다.</p>
              {selectedCard?.status_reason ? <small>{selectedCard.status_reason}</small> : null}
            </>
          )}
        </aside>
      </div>

      <div className="fm-pattern-map__legend">
        <span className="observed">관측 이동</span>
        <span className="forecast">{forecastLegend}</span>
        <span className="uncertainty">{rangeLegend}</span>
        <span className="current">현재 위치</span>
        <small>체제별 확률은 우측에 별도 표시</small>
      </div>
    </section>
  );
}

export default PatternMapSection;
