from __future__ import annotations


def weighted_strategy_role_flags(strategy_names: list[str]) -> dict[str, bool]:
    """Detect common portfolio mix roles from strategy display names."""

    normalized_names = [str(name).lower() for name in strategy_names]
    return {
        "gtaa": any("gtaa" in name for name in normalized_names),
        "equal_weight": any("equal weight" in name for name in normalized_names),
    }
