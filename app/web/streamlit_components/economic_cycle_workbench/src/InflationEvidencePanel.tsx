import type { InflationPolicyPayload } from "./inflationPolicyTypes";

type Props = { payload: InflationPolicyPayload };

function mapping(value: unknown): Record<string, unknown> {
  return value && typeof value === "object" && !Array.isArray(value)
    ? value as Record<string, unknown>
    : {};
}

function text(value: unknown, fallback = "자료 없음") {
  return value == null || value === "" ? fallback : String(value);
}

function evidenceLabel(item: Record<string, unknown>, index: number) {
  return text(item.label || item.series_id || item.source_id, `근거 ${index + 1}`);
}

function InflationEvidencePanel({ payload }: Props) {
  const stateDefinitionVersion = text(
    payload.inflation.state_definition.definition_version
      || payload.inflation.state_definition.version,
  );
  const algorithmVersions = Array.from(new Set(
    payload.rates.resistance_zones
      .map((zone) => zone.algorithm_version)
      .filter(Boolean),
  ));
  const freshnessRows = Object.entries(payload.freshness)
    .map(([seriesId, value]) => ({ seriesId, value: mapping(value) }))
    .filter((row) => Object.keys(row.value).length > 0);

  return (
    <section className="workbench-panel inflation-evidence-boundary" aria-labelledby="inflation-boundary-title">
      <header className="ip-section-heading">
        <div>
          <span>SCOPE · PUBLICATION GUARD</span>
          <h3 id="inflation-boundary-title">현재 연결 범위와 검증 근거</h3>
        </div>
        <small>물가·정책·금리 경로와 독립 침체 모델을 섞지 않습니다.</small>
      </header>

      <div className="model-boundary-grid">
        <article>
          <span>{payload.equity_stress.publication_status === "NOT_AVAILABLE" ? "4차 입력 대기" : "4차 연결"}</span>
          <strong>{payload.equity_stress.publication_status === "NOT_AVAILABLE" ? "주가 스트레스 입력 미충족" : "조건부 주가 스트레스"}</strong>
          <p>{payload.equity_stress.reason}</p>
        </article>
        <article>
          <span>5차 예정</span>
          <strong>침체 모델 미연결</strong>
          <p>{payload.recession.reason}</p>
        </article>
      </div>

      <details className="inflation-evidence-disclosure">
        <summary>
          <div><span>EVIDENCE DISCLOSURE</span><strong>근거·시점·버전 확인</strong></div>
          <small>필요할 때 펼치기</small>
        </summary>
        <div className="inflation-evidence-body">
          <section className="provenance-version-grid" aria-label="모델과 정의 버전">
            <article><span>Snapshot as-of</span><strong>{text(payload.as_of_at)}</strong></article>
            <article><span>모델 버전</span><strong>{text(payload.model_version)}</strong></article>
            <article><span>5상태 정의</span><strong>{stateDefinitionVersion}</strong></article>
            <article>
              <span>금리 기준 알고리즘</span>
              <strong className="algorithm-version-list">
                {algorithmVersions.length
                  ? algorithmVersions.map((version) => <b key={version}>{version}</b>)
                  : "자료 없음"}
              </strong>
            </article>
          </section>

          {payload.evidence.items.length ? (
            <section className="inflation-evidence-list" aria-label="판단 근거 시점">
              <h4>판단 근거</h4>
              {payload.evidence.items.map((raw, index) => {
                const item = mapping(raw);
                return (
                  <article key={`${evidenceLabel(item, index)}:${index}`}>
                    <header><strong>{evidenceLabel(item, index)}</strong><span>{text(item.supports, "지원 영역 없음")}</span></header>
                    <dl>
                      <div><dt>관측일</dt><dd>{text(item.observation_date || item.latest_observation_date)}</dd></div>
                      <div><dt>발표시각</dt><dd>{text(item.released_at || item.latest_released_at)}</dd></div>
                      <div><dt>수집시각</dt><dd>{text(item.collected_at)}</dd></div>
                    </dl>
                  </article>
                );
              })}
            </section>
          ) : <p className="ip-limited-copy">상위 판단 근거가 저장되지 않았습니다. 아래 series 신선도만 확인할 수 있습니다.</p>}

          {freshnessRows.length ? (
            <section className="freshness-clock-list" aria-label="매크로 series 신선도">
              <h4>Series별 데이터 시계</h4>
              {freshnessRows.map(({ seriesId, value }) => (
                <article key={seriesId}>
                  <strong>{seriesId}</strong>
                  <span>관측일 {text(value.latest_observation_date || value.observation_date)}</span>
                  <span>발표시각 {text(value.latest_released_at || value.released_at)}</span>
                  <span>수집시각 {text(value.collected_at)}</span>
                </article>
              ))}
            </section>
          ) : <p className="ip-limited-copy">Series별 신선도 정보가 저장되지 않았습니다.</p>}

          {payload.warnings.length ? (
            <section className="inflation-warning-list" aria-label="검증 제한 사항">
              <h4>검증 제한 사항</h4>
              <ul>{payload.warnings.map((warning, index) => <li key={`${warning}:${index}`}>{warning}</li>)}</ul>
            </section>
          ) : null}
        </div>
      </details>
    </section>
  );
}

export default InflationEvidencePanel;
