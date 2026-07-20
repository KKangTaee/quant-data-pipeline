import { useState } from "react";
import type {
  HorizonCard,
  OutlookHorizonCard,
  PatternMapPayload,
  PatternPoint,
} from "./FuturesMacroWorkbench";

const WIDTH = 720;
const HEIGHT = 390;
const PAD_X = 64;
const PAD_Y = 34;
const DOMAIN_MIN = -2.5;
const DOMAIN_MAX = 2.5;

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

function clipValue(value: number): number {
  return Math.max(DOMAIN_MIN, Math.min(DOMAIN_MAX, value));
}

function isClipped(point: { x: number; y: number }): boolean {
  return point.x < DOMAIN_MIN || point.x > DOMAIN_MAX || point.y < DOMAIN_MIN || point.y > DOMAIN_MAX;
}

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
  return {
    x1: start.x + unitX * startInset,
    y1: start.y + unitY * startInset,
    x2: start.x + unitX * (startInset + segmentLength),
    y2: start.y + unitY * (startInset + segmentLength),
  };
}

function PatternMapSection({ patternMap, horizons }: { patternMap: PatternMapPayload; horizons: HorizonCard[] }) {
  const [selectedHorizon, setSelectedHorizon] = useState<SelectedHorizon>("5D");
  const trail = patternMap.path.slice(-30);
  const anchors = observedAnchors(trail);
  const latest = trail.at(-1);
  const selected = horizons.find((item) => item.key === selectedHorizon);
  const selectedCard: OutlookHorizonCard | undefined = selected?.kind === "conditional_outlook" ? selected : undefined;
  const probabilities = selectedCard?.probabilities || [];
  const sortedRegions = [...(selectedCard?.terminal_regions || [])].sort((left, right) => right.mass - left.mass);
  const directionVector = selectedCard?.vector_status === "VERIFIED"
    ? selectedCard.direction_vector
    : undefined;
  const xScale = (WIDTH - PAD_X * 2) / (DOMAIN_MAX - DOMAIN_MIN);
  const yScale = (HEIGHT - PAD_Y * 2) / (DOMAIN_MAX - DOMAIN_MIN);
  const sx = (value: number) => PAD_X + (clipValue(value) - DOMAIN_MIN) * xScale;
  const sy = (value: number) => HEIGHT - PAD_Y - (clipValue(value) - DOMAIN_MIN) * yScale;
  const vectorTerminal = latest && directionVector
    ? { x: latest.x + directionVector.median_dx, y: latest.y + directionVector.median_dy }
    : undefined;
  const forecastDirection = directionSegment(
    latest ? { x: sx(latest.x), y: sy(latest.y) } : undefined,
    vectorTerminal ? { x: sx(vectorTerminal.x), y: sy(vectorTerminal.y) } : undefined,
    { startInset: 13, endInset: 8, length: 52 },
  );
  const coordinateStatus = selectedCard?.coordinate_status || "UNAVAILABLE";
  const probabilityStatus = selectedCard?.probability_status || "UNAVAILABLE";

  return (
    <section className="fm-workbench__pattern-map" aria-labelledby="fm-pattern-map-title">
      <div className="fm-workbench__section-heading fm-pattern-map__heading">
        <div><span>Observed + probabilistic outlook</span><h3 id="fm-pattern-map-title">최근 시장 위치와 조건부 다음 경로</h3></div>
        <div className="fm-pattern-map__controls" aria-label="전망 기간 선택">
          <button type="button" data-horizon="observed" aria-pressed={selectedHorizon === "observed"} onClick={() => setSelectedHorizon("observed")}>관측만</button>
          <button type="button" data-horizon="5D" aria-pressed={selectedHorizon === "5D"} onClick={() => setSelectedHorizon("5D")}>다음 5D</button>
          <button type="button" data-horizon="20D" aria-pressed={selectedHorizon === "20D"} onClick={() => setSelectedHorizon("20D")}>다음 20D</button>
        </div>
      </div>

      <div className="fm-pattern-map__body">
        <div className="fm-pattern-map__canvas">
          <svg role="img" viewBox={`0 0 ${WIDTH} ${HEIGHT}`} aria-label="최근 30개 완료 세션의 실제 이동과 검증된 확률적 도착 범위">
            <defs>
              <clipPath id="fm-pattern-domain-clip">
                <rect x={PAD_X} y={PAD_Y} width={WIDTH - PAD_X * 2} height={HEIGHT - PAD_Y * 2} />
              </clipPath>
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

            {selectedHorizon !== "observed" ? sortedRegions.map((region) => (
              <ellipse
                className={`fm-pattern-map__terminal-region mass-${Math.round(region.mass * 100)}`}
                data-region-mass={region.mass}
                key={`region-${selectedHorizon}-${region.mass}`}
                cx={sx(region.center_x)}
                cy={sy(region.center_y)}
                clipPath="url(#fm-pattern-domain-clip)"
                rx={Math.max(1, region.radius_major * xScale)}
                ry={Math.max(1, region.radius_minor * yScale)}
                transform={`rotate(${region.rotation_deg} ${sx(region.center_x)} ${sy(region.center_y)})`}
              >
                <title>{selectedHorizon} 검증된 도착 분포 · joint {region.mass === 0.8 ? "80%" : "50%"}</title>
              </ellipse>
            )) : null}

            {trail.slice(1).map((point, index) => {
              const prior = trail[index];
              const opacity = 0.18 + 0.72 * ((index + 1) / Math.max(1, trail.length - 1));
              return (
                <line
                  className="fm-pattern-map__observed-segment"
                  key={`trail-${prior.date}-${point.date}`}
                  x1={sx(prior.x)}
                  y1={sy(prior.y)}
                  x2={sx(point.x)}
                  y2={sy(point.y)}
                  style={{ opacity }}
                >
                  <title>{prior.date} → {point.date}</title>
                </line>
              );
            })}

            {forecastDirection ? (
              <line
                className="fm-pattern-map__direction is-forecast"
                data-direction="forecast"
                {...forecastDirection}
                markerEnd="url(#fm-forecast-direction-arrow)"
              >
                <title>{selectedHorizon} 검증 방향 vector</title>
              </line>
            ) : null}

            {trail.map((point, index) => {
              const clipped = isClipped(point);
              const opacity = 0.24 + 0.66 * ((index + 1) / Math.max(1, trail.length));
              return (
                <g className={`fm-pattern-map__trail-point ${clipped ? "is-clipped" : ""}`} key={`point-${point.date}`} style={{ opacity }}>
                  {clipped ? (
                    <polygon points={`${sx(point.x)},${sy(point.y) - 5} ${sx(point.x) - 5},${sy(point.y) + 5} ${sx(point.x) + 5},${sy(point.y) + 5}`} />
                  ) : (
                    <circle cx={sx(point.x)} cy={sy(point.y)} r={index === trail.length - 1 ? 5 : 2.5} />
                  )}
                  <title>{point.date} · raw ({point.x.toFixed(3)}, {point.y.toFixed(3)}) · {point.regime_label}</title>
                </g>
              );
            })}

            {anchors.map((point) => (
              <g className={`fm-pattern-map__anchor ${point.anchorLabel === "현재" ? "is-current" : ""} ${isClipped(point) ? "is-clipped" : ""}`} key={`anchor-${point.date}-${point.anchorLabel}`}>
                <circle cx={sx(point.x)} cy={sy(point.y)} r={point.anchorLabel === "현재" ? 9 : 6.5} />
                <line className="fm-pattern-map__leader" x1={sx(point.x)} y1={sy(point.y) - 7} x2={sx(point.x)} y2={sy(point.y) - 19} />
                <text x={sx(point.x)} y={sy(point.y) - 23} textAnchor="middle">{point.anchorLabel} · {point.date}</text>
                <title>{point.anchorLabel} · {point.date} · raw ({point.x.toFixed(3)}, {point.y.toFixed(3)}) · {point.regime_label}</title>
              </g>
            ))}
          </svg>
          <span className="fm-pattern-map__x-label">{patternMap.x_label} 강화 →</span>
          <span className="fm-pattern-map__y-label">{patternMap.y_label} 강화 →</span>
        </div>

        <aside className="fm-pattern-map__reading" aria-live="polite">
          {selectedHorizon === "observed" ? (
            <>
              <span>완료 세션 관측</span>
              <strong>최근 {trail.length}개 final session의 실제 일별 이동</strong>
              <dl>
                {anchors.map((point) => <div key={`reading-${point.date}`}><dt>{point.anchorLabel} · {point.date}</dt><dd>{point.regime_label}</dd></div>)}
              </dl>
              <p>20D·5D·현재는 보조 표식이며, 실선은 사이의 모든 일별 관측을 포함합니다.</p>
            </>
          ) : (
            <>
              <div className="fm-pattern-map__reading-head">
                <span>다음 {selectedHorizon} · 조건부 전망</span>
                <b className={`estimate-${probabilityStatus.toLowerCase()}`}>{probabilityStatus}</b>
              </div>
              <strong>{selectedCard?.edge_label || "방향 우위 미확인"}</strong>
              {probabilities.length > 0 ? (
                <dl>
                  {probabilities.map((row) => <div key={`probability-${row.key}`}><dt>{row.label}</dt><dd>{Math.round(row.value * 100)}%</dd></div>)}
                </dl>
              ) : <div className="fm-pattern-map__unavailable">{probabilityStatus === "NO_EDGE" ? "baseline 대비 예측 우위 없음" : "검증 중 · 확정 우위 없음"}</div>}
              {sortedRegions.length > 0 ? (
                <p>ellipse는 검증된 확률적 도착 범위(joint 80% / joint 50%)이며 실제 이동 경로가 아닙니다.</p>
              ) : (
                <div className="fm-pattern-map__unavailable">좌표 상태 {coordinateStatus} · 검증된 도착 분포를 표시하지 않습니다.</div>
              )}
              <p>후보 {selectedCard?.selected_candidate || "선택 없음"} · macro {selectedCard?.macro_adjustment?.used ? "조건 반영" : "미반영"} · 독립 표본 {selectedCard?.episode_count || 0}개</p>
              {selectedCard?.status_reason ? <small>{selectedCard.status_reason}</small> : null}
            </>
          )}
        </aside>
      </div>

      <div className="fm-pattern-map__legend">
        <span className="observed">실제 일별 관측 trail</span>
        <span className="region-80">검증된 joint 80%</span>
        <span className="region-50">검증된 joint 50%</span>
        <span className="forecast">검증된 방향 vector</span>
        <span className="current">현재 위치</span>
        <small>고정 축 -2.5 ~ +2.5 · 경계 삼각형은 범위 밖 raw 값</small>
      </div>
    </section>
  );
}

export default PatternMapSection;
