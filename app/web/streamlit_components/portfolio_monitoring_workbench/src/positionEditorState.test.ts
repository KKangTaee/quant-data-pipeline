import { describe, expect, it } from "vitest";
import {
  applyCloseDefault,
  buildPositionCommandEvent,
  changeTradeDate,
  createPositionEditorDraft,
  markManualExecutionPrice,
  normalizePositionEditorRecovery,
  validatePositionEditorDraft,
} from "./positionEditorState";

describe("position editor state", () => {
  it("fills the exact close by default and resets it when the trade date changes", () => {
    const draft = createPositionEditorDraft("record", "buy", "command-1");
    const first = applyCloseDefault(
      { ...draft, tradeDate: "2026-07-17" },
      {
        status: "READY",
        monitoring_item_id: "item-amd",
        trade_date: "2026-07-17",
        reference_close: 160,
        reason: null,
      },
    );
    expect(first.executionPrice).toBe("160");
    expect(first.priceMode).toBe("db_close_default");

    const manual = markManualExecutionPrice(first, "159.25");
    expect(manual.priceMode).toBe("manual_override");

    const changed = changeTradeDate(manual, "2026-07-18");
    expect(changed.executionPrice).toBe("");
    expect(changed.priceMode).toBe("awaiting_close");
  });

  it("blocks full sell and emits the final execution price", () => {
    const draft = {
      ...createPositionEditorDraft("record", "sell", "command-2"),
      tradeDate: "2026-07-17",
      quantity: "5",
      executionPrice: "159.25",
      feeUsd: "1",
      priceMode: "manual_override" as const,
    };

    expect(
      validatePositionEditorDraft(draft, { currentShares: 5 }),
    ).toContain("최소 1주");
    expect(
      buildPositionCommandEvent({ ...draft, quantity: "4" }, "item-amd"),
    ).toMatchObject({
      id: "record_position_trade",
      monitoring_item_id: "item-amd",
      position_effect: "sell",
      trade_date: "2026-07-17",
      quantity: 4,
      execution_price: 159.25,
      fee_usd: 1,
    });
  });

  it("builds correction and replace command identities", () => {
    const correction = {
      ...createPositionEditorDraft("correct_initial", "buy", "correct-1"),
      quantity: "42",
    };
    expect(buildPositionCommandEvent(correction, "item-amd")).toMatchObject({
      id: "correct_initial_quantity",
      quantity: 42,
    });

    const replacement = {
      ...createPositionEditorDraft("replace", "buy", "replace-1"),
      rootEventId: "buy-root",
      expectedEventId: "buy-v1",
      tradeDate: "2026-07-17",
      quantity: "2",
      executionPrice: "160",
      priceMode: "db_close_default" as const,
    };
    expect(buildPositionCommandEvent(replacement, "item-amd")).toMatchObject({
      id: "replace_position_trade",
      root_event_id: "buy-root",
      expected_event_id: "buy-v1",
    });
  });

  it("preserves the DB-close source across a Streamlit rerun", () => {
    const recovered = normalizePositionEditorRecovery({
      open: true,
      mode: "record",
      position_effect: "buy",
      trade_date: "2026-07-17",
      quantity: "2",
      execution_price: "160",
      price_mode: "db_close_default",
      fee_usd: "0",
      note: "",
      root_event_id: "",
      expected_event_id: "",
    }, "recovered-1");

    expect(recovered?.priceMode).toBe("db_close_default");
  });
});
