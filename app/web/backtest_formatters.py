from __future__ import annotations


def parse_manual_tickers(text: str) -> list[str]:
    seen: set[str] = set()
    tickers: list[str] = []

    for raw in text.split(","):
        symbol = raw.strip().upper()
        if not symbol or symbol in seen:
            continue
        seen.add(symbol)
        tickers.append(symbol)

    return tickers


def format_currency(value: float) -> str:
    return f"${value:,.1f}"


def format_percent(value: float) -> str:
    return f"{value * 100:.2f}%"


def format_ratio(value: float) -> str:
    return f"{value:.3f}"
