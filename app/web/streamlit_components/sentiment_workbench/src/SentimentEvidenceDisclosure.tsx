import { displayValue, signedValue } from "./SentimentWorkbench";
import type { SentimentWorkbenchPayload } from "./SentimentWorkbench";

type EvidenceRows = Record<string, number | string | null | undefined>[];

function rowColumns(rows: EvidenceRows) {
  const keys: string[] = [];
  rows.forEach((row) => Object.keys(row).forEach((key) => {
    if (!keys.includes(key)) keys.push(key);
  }));
  return keys.slice(0, 7);
}

function EvidenceTable({ rows, title }: { rows: EvidenceRows; title: string }) {
  const columns = rowColumns(rows);
  return (
    <div className="sentiment-workbench__evidence-table">
      <div className="sentiment-workbench__evidence-table-title"><span>{title}</span><strong>{rows.length}</strong></div>
      {rows.length === 0 || columns.length === 0 ? (
        <p className="sentiment-workbench__empty">표시할 저장 근거가 없습니다.</p>
      ) : (
        <div className="sentiment-workbench__evidence-scroll">
          <table>
            <thead><tr>{columns.map((column) => <th key={column}>{column}</th>)}</tr></thead>
            <tbody>
              {rows.map((row, rowIndex) => (
                <tr key={`${title}-${rowIndex}`}>
                  {columns.map((column) => <td key={`${title}-${rowIndex}-${column}`}>{displayValue(row[column])}</td>)}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

type Props = {
  payload: SentimentWorkbenchPayload;
  onToggle: () => void;
};

function SentimentEvidenceDisclosure({ payload, onToggle }: Props) {
  return (
    <details className="sentiment-workbench__raw-disclosure" onToggle={onToggle}>
      <summary>상세 근거와 원본 데이터</summary>
      <div className="sentiment-workbench__evidence-columns">
        <article className="sentiment-workbench__cnn-evidence">
          <header><div><strong>CNN 구성요소</strong><small>시장 행동의 내부 근거</small></div><span>{payload.evidence.cnn_components.length}</span></header>
          {payload.evidence.cnn_components.map((item) => (
            <div className="sentiment-workbench__cnn-evidence-row" key={item.series}>
              <div><strong>{item.label_ko || item.series}</strong><small>{item.what_it_checks}</small></div>
              <div>
                <b>{displayValue(item.score)}</b>
                <span
                  className="sentiment-workbench__cnn-status-badge"
                  data-tone={item.tone || "neutral"}
                >
                  {item.rating || "-"}
                </span>
              </div>
              <p>{item.current_reading}</p>
              <small className="sentiment-workbench__evidence-change">직전 대비 {signedValue(item.change, "p")}</small>
            </div>
          ))}
        </article>
        <article className="sentiment-workbench__aaii-evidence">
          <header><div><strong>AAII 장기평균 비교</strong><small>개인투자자 인식의 기준점</small></div><span>{payload.evidence.aaii_comparison.length}</span></header>
          {payload.evidence.aaii_comparison.map((item) => (
            <div className="sentiment-workbench__aaii-row" key={item.key}>
              <strong>{item.label}</strong>
              <div><b>{displayValue(item.current, "%")}</b><span>장기평균 {displayValue(item.historical_average, "%")}</span></div>
              <em>{signedValue(item.difference_pp, "pp")}</em>
            </div>
          ))}
        </article>
      </div>
      {payload.raw_evidence.warnings.length ? <div className="sentiment-workbench__warnings">{payload.raw_evidence.warnings.map((warning) => <span key={warning}>{warning}</span>)}</div> : null}
      <div className="sentiment-workbench__raw-grid">
        <EvidenceTable rows={payload.raw_evidence.sentiment_rows} title="Sentiment rows" />
        <EvidenceTable rows={payload.raw_evidence.component_rows} title="Component rows" />
        <EvidenceTable rows={payload.raw_evidence.history_rows} title="History rows" />
      </div>
      <p className="sentiment-workbench__fallback-note">{payload.boundary_note}</p>
    </details>
  );
}

export default SentimentEvidenceDisclosure;
