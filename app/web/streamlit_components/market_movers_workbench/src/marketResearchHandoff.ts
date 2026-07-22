export type StockResearchHandoffEvent = {
  id: "open_us_stock_research";
  symbol: string;
};

export function buildStockResearchHandoffEvent(symbol: string): StockResearchHandoffEvent {
  return {
    id: "open_us_stock_research",
    symbol: symbol.trim().toUpperCase(),
  };
}
