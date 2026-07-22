import { FormEvent, useEffect, useMemo, useState } from "react";
import type {
  CommandProjection,
  InitialPositionEntryProjection,
  PositionEditorRecoveryState,
  PositionEventRow,
  PositionTradeCloseProjection,
  SelectedPositionProjection,
} from "./contracts";
import {
  applyCloseDefault,
  buildPositionCommandEvent,
  buildPositionEditorRecovery,
  canRequestInitialEntryPreview,
  changeTradeDate,
  createPositionEditorDraft,
  markManualExecutionPrice,
  matchesInitialEntryPreview,
  normalizePositionEditorRecovery,
  positionEditorRecoveryKey,
  validatePositionEditorDraft,
} from "./positionEditorState";
import type { PositionEditorDraft } from "./positionEditorState";

type Props = {
  position: SelectedPositionProjection;
  closeProjection: PositionTradeCloseProjection | null;
  initialProjection: InitialPositionEntryProjection | null;
  recoveryState: PositionEditorRecoveryState | null | undefined;
  latestCommand: CommandProjection | null;
  emit: (event: Record<string, unknown>) => void;
};

function commandId() {
  const token = typeof crypto !== "undefined" && "randomUUID" in crypto
    ? crypto.randomUUID()
    : `${Date.now()}-${Math.random().toString(16).slice(2)}`;
  return `position-${token}`;
}

function money(value: number | null) {
  if (value == null || !Number.isFinite(value)) return "-";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 2,
  }).format(value);
}

function percent(value: number | null) {
  if (value == null || !Number.isFinite(value)) return "-";
  return new Intl.NumberFormat("ko-KR", {
    style: "percent",
    maximumFractionDigits: 2,
  }).format(value);
}

function effectLabel(effect: PositionEventRow["position_effect"]) {
  if (effect === "buy") return "추가매수";
  if (effect === "sell") return "일부매도";
  return "최초 설정 정정";
}

function statusLabel(status: PositionEventRow["status"]) {
  if (status === "superseded") return "수정 전";
  if (status === "voided") return "취소됨";
  return "반영 중";
}

export function PositionLedgerPanel({
  position,
  closeProjection,
  initialProjection,
  recoveryState,
  latestCommand,
  emit,
}: Props) {
  const recoveryKey = positionEditorRecoveryKey(recoveryState);
  const recoveryCommandId = useMemo(commandId, [recoveryKey]);
  const recovered = normalizePositionEditorRecovery(
    recoveryState,
    recoveryCommandId,
  );
  const [draft, setDraft] = useState<PositionEditorDraft | null>(recovered);

  useEffect(() => {
    const next = normalizePositionEditorRecovery(recoveryState, commandId());
    if (next) setDraft(next);
  }, [recoveryKey]);

  useEffect(() => {
    if (!draft || draft.mode === "correct_initial") return;
    const next = applyCloseDefault(draft, closeProjection);
    if (next !== draft) setDraft(next);
  }, [closeProjection?.status, closeProjection?.trade_date, closeProjection?.reference_close]);

  useEffect(() => {
    if (!draft || latestCommand?.command_id !== draft.commandId) return;
    if (["success", "succeeded"].includes(latestCommand.status)) setDraft(null);
  }, [latestCommand?.command_id, latestCommand?.status]);

  if (!position.monitoring_item_id) return null;
  const itemId = position.monitoring_item_id;
  const currentShares = position.current_shares;
  const hasLedger = position.current_shares != null
    && position.effective_initial_shares != null;
  const initialEntryReady = draft
    ? matchesInitialEntryPreview(draft, initialProjection, itemId)
    : false;
  const canRequestInitialPreview = draft
    ? canRequestInitialEntryPreview(draft)
    : false;
  const initialProjectionMatchesDraft = draft?.mode === "correct_initial"
    && initialProjection?.monitoring_item_id === itemId
    && initialProjection.requested_start_date === draft.tradeDate
    && initialProjection.quantity === Number(draft.quantity);
  const validation = draft
    ? validatePositionEditorDraft(draft, {
      currentShares,
      initialEntryReady,
    })
    : null;
  const sellAfter = draft?.mode === "record"
    && draft.positionEffect === "sell"
    && Number.isInteger(Number(draft.quantity))
    && currentShares != null
    ? currentShares - Number(draft.quantity)
    : null;

  const requestInitialEntryPreview = () => {
    if (!draft || !canRequestInitialEntryPreview(draft)) return;
    emit({
      id: "lookup_initial_position_entry",
      monitoring_item_id: itemId,
      requested_start_date: draft.tradeDate,
      quantity: Number(draft.quantity),
      position_editor_state: buildPositionEditorRecovery(draft),
    });
  };
  const openCorrection = () => {
    const next = createPositionEditorDraft(
      "correct_initial", "buy", commandId(),
    );
    setDraft({
      ...next,
      tradeDate: position.requested_start_date ?? "",
      quantity: String(position.effective_initial_shares ?? ""),
    });
  };
  const openTrade = (
    effect: "buy" | "sell" = "buy",
    row?: PositionEventRow,
  ) => {
    const next = createPositionEditorDraft(
      row ? "replace" : "record",
      effect,
      commandId(),
    );
    setDraft(row ? {
      ...next,
      rootEventId: row.root_event_id,
      expectedEventId: row.current_event_id,
      tradeDate: row.trade_date,
      quantity: String(row.quantity ?? ""),
      executionPrice: String(row.execution_price ?? ""),
      feeUsd: String(row.fee_usd ?? 0),
      note: row.note,
      priceMode: row.execution_price_source ?? "awaiting_close",
    } : next);
  };
  const requestClose = (next: PositionEditorDraft) => {
    setDraft(next);
    if (!next.tradeDate) return;
    emit({
      id: "lookup_position_trade_close",
      monitoring_item_id: itemId,
      trade_date: next.tradeDate,
      position_editor_state: buildPositionEditorRecovery(next),
    });
  };
  const submit = (event: FormEvent) => {
    event.preventDefault();
    if (!draft || validation) return;
    emit(buildPositionCommandEvent(draft, itemId));
  };
  const voidTrade = (row: PositionEventRow) => {
    if (!window.confirm(`${effectLabel(row.position_effect)} 기록을 취소할까요? 과거 revision은 감사 이력으로 유지됩니다.`)) return;
    emit({
      id: "void_position_trade",
      command_id: commandId(),
      monitoring_item_id: itemId,
      root_event_id: row.root_event_id,
      expected_event_id: row.current_event_id,
    });
  };

  return (
    <section className="pm-position-ledger" aria-label="개별종목 보유내역">
      <header className="pm-position-heading">
        <div><span>POSITION LEDGER</span><h3>보유내역</h3></div>
        {position.eligible && (
          <div className="pm-position-actions">
            <button type="button" onClick={openCorrection}>최초 설정 정정</button>
            <button type="button" className="is-primary" onClick={() => openTrade()}>매수·매도 기록</button>
          </div>
        )}
      </header>

      {hasLedger && (
        <div className="pm-position-summary">
          <article><span>현재 보유수량</span><strong>{position.current_shares}주</strong><small>최초 {position.effective_initial_shares}주</small></article>
          <article><span>누적 입금</span><strong>{money(position.gross_contributions)}</strong><small>최초 투자금 + 추가매수</small></article>
          <article><span>누적 출금</span><strong>{money(position.gross_withdrawals)}</strong><small>일부매도 순대금</small></article>
          <article><span>현재 평가금액</span><strong>{money(position.current_value)}</strong><small>{position.as_of_date ? `${position.as_of_date} 종목 기준` : "남은 주식 + 배당 현금"}</small></article>
          <article className={(position.pnl ?? 0) < 0 ? "is-negative" : "is-positive"}><span>현금흐름 조정 손익</span><strong>{money(position.pnl)}</strong><small>{percent(position.total_return)}</small></article>
        </div>
      )}

      {!position.eligible && position.reason && (
        <p className="pm-position-boundary">{position.reason}</p>
      )}

      {hasLedger && (
        <div className="pm-position-history">
          <div className="pm-position-history-title"><strong>거래 내역</strong><span>{position.event_rows.length}건</span></div>
          {position.event_rows.map((row) => (
            <article key={row.position_event_id} className={`status-${row.status}`}>
              <div className="pm-position-event-main">
                <span>{row.trade_date} · #{row.event_order}</span>
                <strong>{effectLabel(row.position_effect)} {row.quantity == null ? "" : `${row.quantity}주`}</strong>
                <small>{row.execution_price == null ? "시작 수량 기준" : `${money(row.execution_price)} · 수수료 ${money(row.fee_usd)}`}</small>
              </div>
              <div className="pm-position-event-meta">
                <span>{statusLabel(row.status)}</span>
                {row.execution_price_source && <small>{row.execution_price_source === "db_close_default" ? "종가 기본값" : "수동 체결가"}</small>}
                {row.shares_after != null && <small>거래 후 {row.shares_after}주</small>}
              </div>
              {position.eligible && row.status === "active" && row.position_effect !== "initial_quantity_correction" && (
                <div className="pm-position-event-actions">
                  <button type="button" onClick={() => openTrade(row.position_effect === "sell" ? "sell" : "buy", row)}>수정</button>
                  <button type="button" className="is-danger" onClick={() => voidTrade(row)}>취소</button>
                </div>
              )}
            </article>
          ))}
          {!position.event_rows.length && <p>추가 거래가 없습니다. 최초 등록 수량을 기준으로 추적 중입니다.</p>}
        </div>
      )}

      {draft && position.eligible && (
        <div className="pm-position-editor-layer" role="presentation" onMouseDown={(event) => {
          if (event.currentTarget === event.target) setDraft(null);
        }}>
          <form className="pm-position-editor" role="dialog" aria-modal="true" aria-labelledby="pm-position-editor-title" onSubmit={submit}>
            <header>
              <div><span>POSITION UPDATE</span><h3 id="pm-position-editor-title">{draft.mode === "correct_initial" ? "최초 설정 정정" : draft.mode === "replace" ? "거래 수정" : "매수·매도 기록"}</h3></div>
              <button type="button" aria-label="보유내역 입력 닫기" onClick={() => setDraft(null)}>×</button>
            </header>
            <div className="pm-position-editor-body">
              {draft.mode !== "correct_initial" && (
                <fieldset className="pm-position-effect-switch">
                  <legend>거래 유형</legend>
                  <button type="button" className={draft.positionEffect === "buy" ? "is-active" : ""} disabled={draft.mode === "replace"} onClick={() => setDraft({ ...draft, positionEffect: "buy" })}>추가매수</button>
                  <button type="button" className={draft.positionEffect === "sell" ? "is-active" : ""} disabled={draft.mode === "replace"} onClick={() => setDraft({ ...draft, positionEffect: "sell" })}>일부매도</button>
                </fieldset>
              )}
              {draft.mode === "correct_initial" ? (
                <label>새 추적 시작일<input type="date" value={draft.tradeDate} onInput={(event) => setDraft(changeTradeDate(draft, event.currentTarget.value))} /></label>
              ) : (
                <label>거래일<input type="date" value={draft.tradeDate} onChange={(event) => requestClose(changeTradeDate(draft, event.target.value))} /></label>
              )}
              <label>{draft.mode === "correct_initial" ? "새 최초 수량" : "거래 수량"}<input type="number" min="1" step="1" inputMode="numeric" value={draft.quantity} onChange={(event) => {
                const next = { ...draft, quantity: event.target.value };
                setDraft(next);
              }} /></label>
              {draft.mode === "correct_initial" && (
                <div className="pm-initial-preview-action">
                  <button
                    type="button"
                    onClick={requestInitialEntryPreview}
                    disabled={!canRequestInitialPreview || initialEntryReady}
                  >{initialEntryReady ? "변경값 확인 완료" : "변경값 확인"}</button>
                  <small>{initialEntryReady ? "현재 날짜와 수량의 적용값을 확인했습니다." : "달력과 수량을 정한 뒤 적용일·종가·최초 투자금을 확인하세요."}</small>
                </div>
              )}
              {draft.mode !== "correct_initial" && (
                <label>체결가 (USD)<input type="number" min="0.00000001" step="any" value={draft.executionPrice} onChange={(event) => setDraft(markManualExecutionPrice(draft, event.target.value))} />
                  <small>{draft.priceMode === "db_close_default" ? "종가 기본값 · 필요하면 실제 체결가로 수정하세요." : draft.priceMode === "manual_override" ? "수동 체결가 · 비교 기준 종가도 함께 저장됩니다." : closeProjection?.status === "MISSING" ? closeProjection.reason : "거래일을 선택하면 저장된 종가를 불러옵니다."}</small>
                </label>
              )}
              {draft.mode !== "correct_initial" && <label>수수료 (USD)<input type="number" min="0" step="any" value={draft.feeUsd} onChange={(event) => setDraft({ ...draft, feeUsd: event.target.value })} /></label>}
              <label>메모<textarea maxLength={500} value={draft.note} onChange={(event) => setDraft({ ...draft, note: event.target.value })} /></label>
              {draft.positionEffect === "sell" && draft.mode === "record" && <div className="pm-position-preview"><span>매도 전 {currentShares ?? "-"}주</span><strong>매도 후 {sellAfter ?? "-"}주</strong></div>}
              {draft.positionEffect === "sell" && draft.mode === "replace" && <p className="pm-position-note">수정 저장 시 이 거래 시점부터 전체 거래 이력을 다시 검증합니다.</p>}
              {draft.mode === "correct_initial" && (
                <div className="pm-initial-comparison">
                  <article>
                    <strong>변경 전</strong>
                    <span>요청일 <b>{position.requested_start_date ?? "-"}</b></span>
                    <span>적용일 <b>{position.effective_start_date ?? "-"}</b></span>
                    <span>시작 종가 <b>{money(position.entry_close ?? null)}</b></span>
                    <span>최초 투자금 <b>{money(position.initial_capital ?? null)}</b></span>
                  </article>
                  <article>
                    <strong>변경 후</strong>
                    <span>요청일 <b>{draft.tradeDate || "-"}</b></span>
                    <span>적용일 <b>{initialEntryReady ? initialProjection?.effective_start_date : "-"}</b></span>
                    <span>시작 종가 <b>{money(initialEntryReady ? initialProjection?.entry_close ?? null : null)}</b></span>
                    <span>최초 투자금 <b>{money(initialEntryReady ? initialProjection?.initial_capital ?? null : null)}</b></span>
                  </article>
                </div>
              )}
              {draft.mode === "correct_initial" && initialProjectionMatchesDraft && initialProjection?.status === "MISSING" && <p className="pm-position-error">{initialProjection.reason}</p>}
              {draft.mode === "correct_initial" && <p className="pm-position-note">새 적용일부터 전체 거래 이력과 성과를 다시 계산합니다.</p>}
              {validation && <p className="pm-position-error">{validation}</p>}
            </div>
            <footer><button type="button" onClick={() => setDraft(null)}>취소</button><button type="submit" className="is-primary" disabled={Boolean(validation)}>저장</button></footer>
          </form>
        </div>
      )}
    </section>
  );
}
