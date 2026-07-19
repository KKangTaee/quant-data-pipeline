import type {
  CalculationTracePayload,
  CalculationTraceValue,
} from "./FuturesMacroWorkbench";

const TRACE_SECTION_LABELS = {
  scores: "현재 점수 원본",
  components: "점수 구성 기여",
  symbols: "선물 일봉 변화",
} as const;

function formatValue(value: CalculationTraceValue): string {
  if (value === null || value === undefined || value === "") return "-";
  if (typeof value === "number") {
    return Number.isInteger(value)
      ? value.toLocaleString("ko-KR")
      : value.toLocaleString("ko-KR", { maximumFractionDigits: 4 });
  }
  if (typeof value === "boolean") return value ? "예" : "아니오";
  return String(value);
}

function CalculationTraceDisclosure({
  trace,
  onToggle,
}: {
  trace: CalculationTracePayload;
  onToggle: () => void;
}) {
  return (
    <details className="fm-workbench__trace fm-workbench__disclosure" onToggle={onToggle}>
      <summary>원본 데이터 / 계산 추적</summary>
      <div className="fm-workbench__trace-body">
        <p className="fm-workbench__trace-intro">
          상단 판단을 검산하는 compact snapshot입니다. 10년 전체 OHLCV가 아니라 현재 점수와 계산 근거만 표시합니다.
        </p>
        <div className="fm-workbench__trace-metadata">
          {trace.metadata.map((item) => (
            <div key={item.label}>
              <span>{item.label}</span>
              <strong>{item.value || "-"}</strong>
            </div>
          ))}
        </div>
        {trace.tables.map((table) => (
          <section className="fm-workbench__trace-section" data-trace-section={table.key} key={table.key}>
            <header>
              <h4>{table.label || TRACE_SECTION_LABELS[table.key]}</h4>
              <span>{table.rows.length}행</span>
            </header>
            {table.rows.length > 0 && table.columns.length > 0 ? (
              <div className="fm-workbench__trace-table-wrap">
                <table className="fm-workbench__trace-table">
                  <thead>
                    <tr>{table.columns.map((column) => <th key={column}>{column}</th>)}</tr>
                  </thead>
                  <tbody>
                    {table.rows.map((row, rowIndex) => (
                      <tr key={`${table.key}-${rowIndex}`}>
                        {table.columns.map((column) => (
                          <td key={column}>{formatValue(row[column])}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="fm-workbench__empty">저장된 계산 행이 없습니다.</p>
            )}
          </section>
        ))}
        <section className="fm-workbench__trace-section" data-trace-section="cautions">
          <header>
            <h4>해석 주의점</h4>
            <span>{trace.cautions.length}개</span>
          </header>
          {trace.cautions.length > 0 ? (
            <ul className="fm-workbench__trace-cautions">
              {trace.cautions.map((item) => <li key={item}>{item}</li>)}
            </ul>
          ) : (
            <p className="fm-workbench__empty">추가 주의점이 없습니다.</p>
          )}
        </section>
      </div>
    </details>
  );
}

export default CalculationTraceDisclosure;
