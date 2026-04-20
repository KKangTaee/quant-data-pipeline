from __future__ import annotations

from collections import OrderedDict


NON_FAMILY_STRATEGY_OPTIONS = [
    "Equal Weight",
    "GTAA",
    "Global Relative Strength",
    "Risk Parity Trend",
    "Dual Momentum",
]

STRATEGY_FAMILY_VARIANTS = {
    "Quality": OrderedDict(
        [
            (
                "Strict Annual",
                {
                    "display_name": "Quality Snapshot (Strict Annual)",
                    "strategy_key": "quality_snapshot_strict_annual",
                },
            ),
            (
                "Strict Quarterly Prototype",
                {
                    "display_name": "Quality Snapshot (Strict Quarterly Prototype)",
                    "strategy_key": "quality_snapshot_strict_quarterly_prototype",
                },
            ),
        ]
    ),
    "Value": OrderedDict(
        [
            (
                "Strict Annual",
                {
                    "display_name": "Value Snapshot (Strict Annual)",
                    "strategy_key": "value_snapshot_strict_annual",
                },
            ),
            (
                "Strict Quarterly Prototype",
                {
                    "display_name": "Value Snapshot (Strict Quarterly Prototype)",
                    "strategy_key": "value_snapshot_strict_quarterly_prototype",
                },
            ),
        ]
    ),
    "Quality + Value": OrderedDict(
        [
            (
                "Strict Annual",
                {
                    "display_name": "Quality + Value Snapshot (Strict Annual)",
                    "strategy_key": "quality_value_snapshot_strict_annual",
                },
            ),
            (
                "Strict Quarterly Prototype",
                {
                    "display_name": "Quality + Value Snapshot (Strict Quarterly Prototype)",
                    "strategy_key": "quality_value_snapshot_strict_quarterly_prototype",
                },
            ),
        ]
    ),
}

SINGLE_STRATEGY_OPTIONS = NON_FAMILY_STRATEGY_OPTIONS + list(STRATEGY_FAMILY_VARIANTS.keys())
COMPARE_STRATEGY_OPTIONS = SINGLE_STRATEGY_OPTIONS

STRATEGY_KEY_TO_DISPLAY_NAME = {
    "equal_weight": "Equal Weight",
    "gtaa": "GTAA",
    "global_relative_strength": "Global Relative Strength",
    "risk_parity_trend": "Risk Parity Trend",
    "dual_momentum": "Dual Momentum",
    "quality_snapshot": "Quality Snapshot",
}
for family_variants in STRATEGY_FAMILY_VARIANTS.values():
    for variant_config in family_variants.values():
        STRATEGY_KEY_TO_DISPLAY_NAME[variant_config["strategy_key"]] = variant_config["display_name"]


def is_family_strategy(option: str | None) -> bool:
    return bool(option and option in STRATEGY_FAMILY_VARIANTS)


def family_variant_options(option: str) -> list[str]:
    return list(STRATEGY_FAMILY_VARIANTS.get(option, {}).keys())


def resolve_concrete_strategy_display_name(option: str, variant: str | None = None) -> str:
    if option in NON_FAMILY_STRATEGY_OPTIONS:
        return option
    family_variants = STRATEGY_FAMILY_VARIANTS.get(option)
    if not family_variants:
        return option
    selected_variant = variant or next(iter(family_variants.keys()))
    return str(family_variants[selected_variant]["display_name"])


def resolve_concrete_strategy_key(option: str, variant: str | None = None) -> str | None:
    display_name = resolve_concrete_strategy_display_name(option, variant)
    return display_name_to_strategy_key(display_name)


def strategy_key_to_display_name(strategy_key: str | None) -> str | None:
    if strategy_key is None:
        return None
    return STRATEGY_KEY_TO_DISPLAY_NAME.get(strategy_key)


def display_name_to_strategy_key(display_name: str | None) -> str | None:
    if display_name is None:
        return None
    for strategy_key, label in STRATEGY_KEY_TO_DISPLAY_NAME.items():
        if label == display_name:
            return strategy_key
    return None


def display_name_to_selection(display_name: str | None) -> tuple[str | None, str | None]:
    if display_name is None:
        return None, None
    if display_name in NON_FAMILY_STRATEGY_OPTIONS:
        return display_name, None
    if display_name in STRATEGY_FAMILY_VARIANTS:
        return display_name, None

    for family_name, family_variants in STRATEGY_FAMILY_VARIANTS.items():
        for variant_name, variant_config in family_variants.items():
            if variant_config["display_name"] == display_name:
                return family_name, variant_name
    return display_name, None


def strategy_key_to_selection(strategy_key: str | None) -> tuple[str | None, str | None]:
    return display_name_to_selection(strategy_key_to_display_name(strategy_key))
