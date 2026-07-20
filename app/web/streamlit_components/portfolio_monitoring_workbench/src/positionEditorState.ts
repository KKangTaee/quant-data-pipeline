import type {
  PositionEditorRecoveryState,
  PositionTradeCloseProjection,
} from "./contracts";

export type PositionEditorDraft = {
  commandId: string;
  mode: "correct_initial" | "record" | "replace";
  rootEventId: string | null;
  expectedEventId: string | null;
  positionEffect: "buy" | "sell";
  tradeDate: string;
  quantity: string;
  executionPrice: string;
  feeUsd: string;
  note: string;
  priceMode: "awaiting_close" | "db_close_default" | "manual_override";
};

export function createPositionEditorDraft(
  mode: PositionEditorDraft["mode"],
  positionEffect: PositionEditorDraft["positionEffect"],
  commandId: string,
): PositionEditorDraft {
  return {
    commandId,
    mode,
    rootEventId: null,
    expectedEventId: null,
    positionEffect,
    tradeDate: "",
    quantity: "",
    executionPrice: "",
    feeUsd: "0",
    note: "",
    priceMode: "awaiting_close",
  };
}

export function normalizePositionEditorRecovery(
  value: PositionEditorRecoveryState | null | undefined,
  commandId: string,
): PositionEditorDraft | null {
  if (!value?.open) return null;
  const mode = value.mode === "correction" ? "correct_initial" : value.mode;
  return {
    commandId,
    mode,
    rootEventId: value.root_event_id || null,
    expectedEventId: value.expected_event_id || null,
    positionEffect: value.position_effect,
    tradeDate: value.trade_date,
    quantity: value.quantity,
    executionPrice: value.execution_price,
    feeUsd: value.fee_usd || "0",
    note: value.note,
    priceMode: value.price_mode,
  };
}

export function applyCloseDefault(
  draft: PositionEditorDraft,
  close: PositionTradeCloseProjection | null | undefined,
): PositionEditorDraft {
  if (
    draft.priceMode === "manual_override"
    || close?.status !== "READY"
    || close.trade_date !== draft.tradeDate
    || close.reference_close == null
  ) return draft;
  return {
    ...draft,
    executionPrice: String(close.reference_close),
    priceMode: "db_close_default",
  };
}

export function markManualExecutionPrice(
  draft: PositionEditorDraft,
  executionPrice: string,
): PositionEditorDraft {
  return {
    ...draft,
    executionPrice,
    priceMode: executionPrice ? "manual_override" : "awaiting_close",
  };
}

export function changeTradeDate(
  draft: PositionEditorDraft,
  tradeDate: string,
): PositionEditorDraft {
  return {
    ...draft,
    tradeDate,
    executionPrice: "",
    priceMode: "awaiting_close",
  };
}

export function validatePositionEditorDraft(
  draft: PositionEditorDraft,
  context: { currentShares: number | null },
): string | null {
  const quantity = Number(draft.quantity);
  if (!Number.isInteger(quantity) || quantity < 1) {
    return "수량은 1주 이상의 정수여야 합니다.";
  }
  if (draft.note.length > 500) return "메모는 500자 이하여야 합니다.";
  if (draft.mode === "correct_initial") return null;
  if (!draft.tradeDate) return "거래일을 선택해 주세요.";
  const price = Number(draft.executionPrice);
  if (!Number.isFinite(price) || price <= 0) return "체결가는 0보다 커야 합니다.";
  const fee = Number(draft.feeUsd || "0");
  if (!Number.isFinite(fee) || fee < 0) return "수수료는 0 이상이어야 합니다.";
  if (draft.positionEffect === "sell") {
    if (quantity * price - fee <= 0) return "매도 후 순출금액이 0보다 커야 합니다.";
    if (context.currentShares != null && quantity >= context.currentShares) {
      return "일부매도 후 최소 1주를 유지해야 합니다. 전량매도는 추적 종료를 이용해 주세요.";
    }
  }
  if (draft.mode === "replace" && (!draft.rootEventId || !draft.expectedEventId)) {
    return "수정할 최신 거래 기록을 찾을 수 없습니다.";
  }
  return null;
}

export function buildPositionCommandEvent(
  draft: PositionEditorDraft,
  monitoringItemId: string,
): Record<string, unknown> {
  if (draft.mode === "correct_initial") {
    return {
      id: "correct_initial_quantity",
      command_id: draft.commandId,
      monitoring_item_id: monitoringItemId,
      quantity: Number(draft.quantity),
      note: draft.note,
    };
  }
  return {
    id: draft.mode === "replace"
      ? "replace_position_trade"
      : "record_position_trade",
    command_id: draft.commandId,
    monitoring_item_id: monitoringItemId,
    root_event_id: draft.rootEventId,
    expected_event_id: draft.expectedEventId,
    position_effect: draft.positionEffect,
    trade_date: draft.tradeDate,
    quantity: Number(draft.quantity),
    execution_price: Number(draft.executionPrice),
    fee_usd: Number(draft.feeUsd || "0"),
    note: draft.note,
  };
}

export function buildPositionEditorRecovery(
  draft: PositionEditorDraft,
): PositionEditorRecoveryState {
  return {
    open: true,
    mode: draft.mode === "correct_initial" ? "correction" : draft.mode,
    position_effect: draft.positionEffect,
    trade_date: draft.tradeDate,
    quantity: draft.quantity,
    execution_price: draft.executionPrice,
    price_mode: draft.priceMode,
    fee_usd: draft.feeUsd,
    note: draft.note,
    root_event_id: draft.rootEventId ?? "",
    expected_event_id: draft.expectedEventId ?? "",
  };
}
