import { useEffect, useMemo, useRef, useState } from "react";
import type {
  InflationPolicyCommand,
  InflationPolicyPayload,
  ResistanceZone,
} from "./inflationPolicyTypes";

type Props = {
  payload: InflationPolicyPayload;
  onCommand: (command: InflationPolicyCommand) => void;
};

const INSTRUMENTS = ["DGS10", "DGS2", "DFII10", "T10YIE", "T10Y2Y", "ACMTP10"];

function finiteNumber(value: unknown): number | null {
  const parsed = typeof value === "number" ? value : Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function mapping(value: unknown): Record<string, unknown> {
  return value && typeof value === "object" && !Array.isArray(value)
    ? value as Record<string, unknown>
    : {};
}

function percentage(value: unknown): string {
  const parsed = finiteNumber(value);
  return parsed === null ? "—" : `${(parsed * 100).toFixed(1)}%`;
}

function percentileRows(value: unknown) {
  const values = mapping(value);
  return ["p20", "p50", "p80"].map((key) => ({ key, value: finiteNumber(values[key]) }));
}

function initialZone(payload: InflationPolicyPayload): ResistanceZone | undefined {
  return payload.rates.resistance_zones.find((zone) => zone.owner === "AUTO")
    || payload.rates.resistance_zones[0];
}

function initialTarget(payload: InflationPolicyPayload) {
  const storedTarget = mapping(payload.reverse_scenario.target);
  const fallbackZone = initialZone(payload);
  const lower = finiteNumber(storedTarget.zone_lower_pct);
  const upper = finiteNumber(storedTarget.zone_upper_pct);
  const instrument = String(storedTarget.instrument || fallbackZone?.instrument || "DGS10");
  const matchingZone = payload.rates.resistance_zones.find((candidate) => (
    candidate.instrument === instrument
    && lower !== null
    && upper !== null
    && candidate.zone_lower_pct === lower
    && candidate.zone_upper_pct === upper
  ));
  const condition = String(storedTarget.condition || "CONFIRMED");
  return {
    zone: matchingZone || fallbackZone,
    instrument,
    lower: lower ?? fallbackZone?.zone_lower_pct ?? 4.58,
    upper: upper ?? fallbackZone?.zone_upper_pct ?? 4.65,
    buffer: matchingZone?.buffer_pct ?? fallbackZone?.buffer_pct ?? 0.05,
    condition: ["REACH", "CONFIRMED", "HOLD"].includes(condition)
      ? condition as "REACH" | "CONFIRMED" | "HOLD"
      : "CONFIRMED",
  };
}

function ReverseScenarioPanel({ payload, onCommand }: Props) {
  const target = useMemo(() => initialTarget(payload), [payload]);
  const zone = target.zone;
  const snapshotIdentity = `${payload.as_of_at || ""}|${payload.model_version || ""}`;
  const targetIdentity = [
    target.instrument,
    target.lower,
    target.upper,
    target.buffer,
    target.condition,
  ].join("|");
  const [instrument, setInstrument] = useState(target.instrument);
  const [lower, setLower] = useState(target.lower);
  const [upper, setUpper] = useState(target.upper);
  const [buffer, setBuffer] = useState(target.buffer);
  const [condition, setCondition] = useState<"REACH" | "CONFIRMED" | "HOLD">(target.condition);
  const [formDirty, setFormDirty] = useState(false);
  const [holdDays, setHoldDays] = useState(3);
  const year = /^\d{4}/.test(payload.as_of_at || "") ? String(payload.as_of_at).slice(0, 4) : "2026";
  const [horizon, setHorizon] = useState(`${year}-12-31`);
  const [showSave, setShowSave] = useState(false);
  const [definitionName, setDefinitionName] = useState(zone ? `${zone.definition_name} 사본` : "내 장기금리 기준");
  const [confirmationCount, setConfirmationCount] = useState(3);
  const [confirmationWindow, setConfirmationWindow] = useState(5);
  const [requireBreakeven, setRequireBreakeven] = useState(false);
  const [excludeTermPremiumOnly, setExcludeTermPremiumOnly] = useState(true);
  const previousSnapshotIdentity = useRef(snapshotIdentity);

  useEffect(() => {
    const snapshotChanged = previousSnapshotIdentity.current !== snapshotIdentity;
    if (snapshotChanged || !formDirty) {
      setInstrument(target.instrument);
      setLower(target.lower);
      setUpper(target.upper);
      setBuffer(target.buffer);
      setCondition(target.condition);
      if (snapshotChanged) {
        const snapshotYear = /^\d{4}/.test(payload.as_of_at || "")
          ? String(payload.as_of_at).slice(0, 4)
          : "2026";
        setHoldDays(3);
        setHorizon(`${snapshotYear}-12-31`);
      }
      setFormDirty(false);
    }
    previousSnapshotIdentity.current = snapshotIdentity;
  }, [snapshotIdentity, targetIdentity]);

  const boundsError = lower > upper
    ? "구간 하단은 상단보다 낮아야 합니다."
    : upper - lower > 2
      ? "목표 구간 폭은 200bp 이하여야 합니다."
      : buffer < 0
        ? "확인 buffer는 0 이상이어야 합니다."
        : null;
  const confirmationError = confirmationCount > confirmationWindow
    ? "확인 횟수는 확인 기간을 초과할 수 없습니다."
    : null;
  const reverseResult = payload.command_result?.command_id === "run_reverse_scenario"
    ? payload.command_result
    : payload.reverse_scenario;
  const saveResult = payload.command_result?.command_id === "save_yield_criterion"
    ? payload.command_result
    : null;

  const runReverse = () => {
    if (boundsError) return;
    onCommand({
      id: "run_reverse_scenario",
      nonce: `run_reverse_scenario:${Date.now()}`,
      payload: {
        instrument,
        zone_lower_pct: lower,
        zone_upper_pct: upper,
        buffer_pct: buffer,
        condition,
        hold_days: holdDays,
        horizon_at: `${horizon}T23:59:59Z`,
        as_of_at: payload.as_of_at,
      },
    });
  };

  const saveCriterion = () => {
    if (boundsError || confirmationError || !definitionName.trim()) return;
    onCommand({
      id: "save_yield_criterion",
      nonce: `save_yield_criterion:${Date.now()}`,
      payload: {
        owner: "USER",
        definition_name: definitionName.trim(),
        instrument,
        zone_lower_pct: lower,
        zone_upper_pct: upper,
        buffer_pct: buffer,
        short_lookback_days: 63,
        long_lookback_days: 504,
        confirmation_count: confirmationCount,
        confirmation_window: confirmationWindow,
        require_breakeven_confirmation: requireBreakeven,
        exclude_term_premium_only: excludeTermPremiumOnly,
        as_of_at: payload.as_of_at,
      },
    });
  };

  return (
    <section className="workbench-panel reverse-scenario-panel" aria-labelledby="reverse-scenario-title">
      <header className="ip-section-heading">
        <div>
          <span>REVERSE · CONDITIONAL PATHS</span>
          <h3 id="reverse-scenario-title">금리 목표에서 필요한 공동 경로 역산</h3>
        </div>
        <small>목표를 만족한 경로의 물가·정책 분포를 봅니다. 인상 횟수를 단일 정답으로 확정하지 않습니다.</small>
      </header>

      <div className="reverse-workspace-grid">
        <form className="reverse-target-form" onSubmit={(event) => { event.preventDefault(); runReverse(); }}>
          <label>
            <span>금리 종류</span>
            <select value={instrument} onChange={(event) => { setInstrument(event.target.value); setFormDirty(true); }}>
              {INSTRUMENTS.map((item) => <option key={item} value={item}>{item}</option>)}
            </select>
          </label>
          <div className="reverse-bound-grid">
            <label>
              <span>구간 하단</span>
              <input type="number" min="0" max="20" step="0.01" value={lower} onChange={(event) => { setLower(Number(event.target.value)); setFormDirty(true); }} />
            </label>
            <label>
              <span>구간 상단</span>
              <input type="number" min="0" max="20" step="0.01" value={upper} onChange={(event) => { setUpper(Number(event.target.value)); setFormDirty(true); }} />
            </label>
            <label>
              <span>확인 buffer</span>
              <input type="number" min="0" max="2" step="0.01" value={buffer} onChange={(event) => { setBuffer(Number(event.target.value)); setFormDirty(true); }} />
            </label>
          </div>
          <div className="reverse-bound-grid">
            <label>
              <span>확인 조건</span>
              <select value={condition} onChange={(event) => { setCondition(event.target.value as "REACH" | "CONFIRMED" | "HOLD"); setFormDirty(true); }}>
                <option value="REACH">구간 도달</option>
                <option value="CONFIRMED">상단 돌파 확인</option>
                <option value="HOLD">돌파 후 유지</option>
              </select>
            </label>
            <label>
              <span>확인 일수</span>
              <input type="number" min="1" max="20" step="1" value={holdDays} onChange={(event) => { setHoldDays(Number(event.target.value)); setFormDirty(true); }} />
            </label>
            <label>
              <span>분석 horizon</span>
              <input type="date" value={horizon} onChange={(event) => { setHorizon(event.target.value); setFormDirty(true); }} />
            </label>
          </div>
          {boundsError ? <p className="ip-form-error" role="alert">{boundsError}</p> : null}
          <div className="reverse-form-actions">
            <button className="ip-primary-action" type="submit" disabled={Boolean(boundsError || !horizon)}>필요 경로 역산</button>
            <button className="ip-secondary-action" type="button" onClick={() => setShowSave(true)}>사용자 기준으로 복사</button>
          </div>
          <p className="reverse-form-note">현재 자동 구간은 추천값이며 직접 수정되지 않습니다. 입력값은 이번 역산 또는 별도 사용자 기준에만 적용됩니다.</p>
        </form>

        <section className={`reverse-result-card status-${String(reverseResult.publication_status || "NOT_AVAILABLE").toLowerCase()}`} aria-live="polite">
          {reverseResult.publication_status === "READY" ? (
            <ReverseReadyResult result={reverseResult} />
          ) : (
            <>
              <span>CONDITIONAL DISTRIBUTION</span>
              <strong>공동 경로 검증 전</strong>
              <p>{String(reverseResult.reason || "선택한 목표를 만족하는 검증 경로를 아직 공개할 수 없습니다.")}</p>
              <small>구간을 넓히거나 horizon을 늘린 뒤에도 검증 표본이 충분한지 확인합니다.</small>
            </>
          )}
        </section>
      </div>

      {showSave ? (
        <form className="user-criterion-form" onSubmit={(event) => { event.preventDefault(); saveCriterion(); }}>
          <header>
            <div><span>USER OWNED</span><strong>별도 사용자 기준 저장</strong></div>
            <button type="button" aria-label="사용자 기준 저장 닫기" onClick={() => setShowSave(false)}>닫기</button>
          </header>
          <div className="user-criterion-fields">
            <label className="criterion-name-field">
              <span>기준 이름</span>
              <input value={definitionName} onChange={(event) => setDefinitionName(event.target.value)} />
            </label>
            <label>
              <span>확인 횟수</span>
              <input type="number" min="1" max="20" value={confirmationCount} onChange={(event) => setConfirmationCount(Number(event.target.value))} />
            </label>
            <label>
              <span>확인 기간</span>
              <input type="number" min="1" max="20" value={confirmationWindow} onChange={(event) => setConfirmationWindow(Number(event.target.value))} />
            </label>
          </div>
          <div className="criterion-checks">
            <label><input type="checkbox" checked={requireBreakeven} onChange={(event) => setRequireBreakeven(event.target.checked)} /> 기대인플레이션 동행 확인</label>
            <label><input type="checkbox" checked={excludeTermPremiumOnly} onChange={(event) => setExcludeTermPremiumOnly(event.target.checked)} /> 기간 프리미엄 단독 상승 제외</label>
          </div>
          {confirmationError ? <p className="ip-form-error" role="alert">{confirmationError}</p> : null}
          <button className="ip-primary-action" type="submit" disabled={Boolean(boundsError || confirmationError || !definitionName.trim())}>사용자 기준 저장</button>
          {saveResult ? <p className="ip-form-success">{String(saveResult.message || "사용자 기준을 저장했습니다.")}</p> : null}
        </form>
      ) : null}
    </section>
  );
}

function ReverseReadyResult({ result }: { result: Record<string, unknown> }) {
  const q4 = percentileRows(result.q4_core_pce_quantiles_pct);
  const requiredMom = percentileRows(result.required_remaining_mom_quantiles_pct);
  const policy = mapping(result.policy_net_step_probabilities);
  const sensitivity = Array.isArray(result.next_print_sensitivity) ? result.next_print_sensitivity : [];
  return (
    <>
      <span>CONDITIONAL DISTRIBUTION</span>
      <strong>조건부분포 공개 가능</strong>
      <p>{String(result.reason || "선택한 목표를 만족한 공동 경로의 분포입니다.")}</p>
      <div className="reverse-support-grid">
        <div><span>목표 확률</span><b>{percentage(result.target_probability)}</b></div>
        <div><span>지지 경로</span><b>{finiteNumber(result.supporting_path_count)?.toLocaleString() || "—"}</b></div>
        <div><span>유효 경로</span><b>{finiteNumber(result.effective_path_count)?.toFixed(1) || "—"}</b></div>
      </div>
      <div className="conditional-quantiles">
        <div><span>연말 Core PCE</span>{q4.map((row) => <b key={row.key}>{row.key.toUpperCase()} {row.value?.toFixed(2) || "—"}%</b>)}</div>
        <div><span>남은 월평균 PCE</span>{requiredMom.map((row) => <b key={row.key}>{row.key.toUpperCase()} {row.value?.toFixed(2) || "—"}%</b>)}</div>
      </div>
      {Object.keys(policy).length ? (
        <div className="conditional-policy-list">
          <span>정책 경로 분포</span>
          {Object.entries(policy).map(([key, value]) => <b key={key}>{key} {percentage(value)}</b>)}
        </div>
      ) : null}
      {sensitivity.length ? (
        <div className="conditional-sensitivity">
          <span>다음 Core PCE 발표 민감도</span>
          {sensitivity.map((item, index) => {
            const row = mapping(item);
            return <b key={index}>{finiteNumber(row.mom_pct)?.toFixed(1) || "—"}% → {percentage(row.target_probability)}</b>;
          })}
        </div>
      ) : null}
    </>
  );
}

export default ReverseScenarioPanel;
