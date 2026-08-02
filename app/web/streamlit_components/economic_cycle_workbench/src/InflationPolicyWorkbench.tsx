import type { InflationPolicyWorkbenchProps } from "./inflationPolicyTypes";

function InflationPolicyWorkbench({ payload }: InflationPolicyWorkbenchProps) {
  return (
    <main className="inflation-policy-workbench" data-status={payload.publication_status}>
      <header className="inflation-policy-placeholder-hero">
        <span>U.S. INFLATION · POLICY · YIELDS</span>
        <h2>연말 Core PCE 경로</h2>
        <p>{payload.headline.summary}</p>
        <small>{payload.headline.history_label} · {payload.as_of_at || "기준시각 없음"}</small>
      </header>
      {payload.publication_status === "NOT_AVAILABLE" || payload.publication_status === "FAILED" ? (
        <section className="inflation-policy-unavailable" aria-live="polite">
          <strong>현재 공개 가능한 경로가 없습니다.</strong>
          <p>{payload.inflation.reason}</p>
        </section>
      ) : null}
    </main>
  );
}

export default InflationPolicyWorkbench;
