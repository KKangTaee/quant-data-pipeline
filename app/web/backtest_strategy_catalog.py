from __future__ import annotations

from app.services.backtest_strategy_catalog import (
    COMPARE_STRATEGY_OPTIONS,
    NON_FAMILY_STRATEGY_OPTIONS,
    SINGLE_STRATEGY_OPTIONS,
    STRATEGY_FAMILY_VARIANTS,
    STRATEGY_KEY_TO_DISPLAY_NAME,
    display_name_to_selection,
    display_name_to_strategy_key,
    family_variant_options,
    is_family_strategy,
    resolve_concrete_strategy_display_name,
    resolve_concrete_strategy_key,
    strategy_key_to_display_name,
    strategy_key_to_selection,
)

__all__ = [
    "COMPARE_STRATEGY_OPTIONS",
    "NON_FAMILY_STRATEGY_OPTIONS",
    "SINGLE_STRATEGY_OPTIONS",
    "STRATEGY_FAMILY_VARIANTS",
    "STRATEGY_KEY_TO_DISPLAY_NAME",
    "display_name_to_selection",
    "display_name_to_strategy_key",
    "family_variant_options",
    "is_family_strategy",
    "resolve_concrete_strategy_display_name",
    "resolve_concrete_strategy_key",
    "strategy_key_to_display_name",
    "strategy_key_to_selection",
]
