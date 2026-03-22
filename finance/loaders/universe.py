from __future__ import annotations

from collections.abc import Iterable

from ._common import resolve_loader_symbols


def load_universe(
    source: str | None = None,
    *,
    symbols: str | Iterable[str] | None = None,
) -> list[str]:
    """
    Resolve a normalized symbol universe for loader/runtime use.

    Parameters
    ----------
    source:
        Named universe source such as ``nyse_stocks`` or
        ``profile_filtered_stocks``.
    symbols:
        Explicit symbol override. If provided, this takes precedence.
    """
    return resolve_loader_symbols(symbols=symbols, universe_source=source)
