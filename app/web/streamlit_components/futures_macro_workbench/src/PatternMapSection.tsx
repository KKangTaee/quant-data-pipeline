import type { PatternMapPayload } from "./FuturesMacroWorkbench";

const WIDTH = 520;
const HEIGHT = 300;
const PAD = 32;

function PatternMapSection({ patternMap }: { patternMap: PatternMapPayload }) {
  const xs = [...patternMap.path.map((item) => item.x), ...patternMap.zones.flatMap((zone) => [zone.center_x - zone.radius_x, zone.center_x + zone.radius_x]), -1, 1];
  const ys = [...patternMap.path.map((item) => item.y), ...patternMap.zones.flatMap((zone) => [zone.center_y - zone.radius_y, zone.center_y + zone.radius_y]), -1, 1];
  const xMin = Math.min(...xs);
  const xMax = Math.max(...xs);
  const yMin = Math.min(...ys);
  const yMax = Math.max(...ys);
  const sx = (value: number) => PAD + ((value - xMin) / Math.max(0.01, xMax - xMin)) * (WIDTH - PAD * 2);
  const sy = (value: number) => HEIGHT - PAD - ((value - yMin) / Math.max(0.01, yMax - yMin)) * (HEIGHT - PAD * 2);
  const observedPoints = patternMap.path.map((point) => `${sx(point.x)},${sy(point.y)}`).join(" ");
  const latest = patternMap.path.at(-1);

  return (
    <section className="fm-workbench__pattern-map" aria-labelledby="fm-pattern-map-title">
      <div className="fm-workbench__section-heading">
        <div><span>Observed path</span><h3 id="fm-pattern-map-title">{patternMap.title}</h3></div>
        <small>선은 관측 · 면은 조건부 결과 영역</small>
      </div>
      <div className="fm-pattern-map__canvas">
        <svg role="img" viewBox={`0 0 ${WIDTH} ${HEIGHT}`} aria-label="관측 경로와 조건부 결과 영역">
          <line className="fm-pattern-map__axis" x1={sx(0)} x2={sx(0)} y1={PAD} y2={HEIGHT - PAD} />
          <line className="fm-pattern-map__axis" x1={PAD} x2={WIDTH - PAD} y1={sy(0)} y2={sy(0)} />
          {patternMap.zones.map((zone) => (
            <ellipse
              className={`fm-pattern-map__zone regime-${zone.regime} horizon-${zone.horizon.toLowerCase()}`}
              cx={sx(zone.center_x)}
              cy={sy(zone.center_y)}
              key={`${zone.horizon}-${zone.regime}`}
              opacity={Math.max(0.12, Math.min(0.58, zone.probability))}
              rx={Math.max(18, Math.abs(sx(zone.center_x + zone.radius_x) - sx(zone.center_x)))}
              ry={Math.max(14, Math.abs(sy(zone.center_y + zone.radius_y) - sy(zone.center_y)))}
            >
              <title>{zone.horizon} 조건부 결과 영역 · {Math.round(zone.probability * 100)}%</title>
            </ellipse>
          ))}
          {observedPoints ? <polyline className="fm-pattern-map__observed" points={observedPoints} /> : null}
          {latest ? <circle className={`fm-pattern-map__latest regime-${latest.regime}`} cx={sx(latest.x)} cy={sy(latest.y)} r="6"><title>현재 · {latest.regime_label} · {latest.transition_label}</title></circle> : null}
        </svg>
        <span className="fm-pattern-map__x-label">{patternMap.x_label} →</span>
        <span className="fm-pattern-map__y-label">{patternMap.y_label} →</span>
      </div>
      <div className="fm-pattern-map__legend"><span className="observed">관측 경로</span><span className="zone-5d">5D 영역</span><span className="zone-20d">20D 영역</span></div>
    </section>
  );
}

export default PatternMapSection;
