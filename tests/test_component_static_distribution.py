from __future__ import annotations

import re
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
COMPONENT_ROOT = REPO_ROOT / "app" / "web" / "components"
BACKTEST_COMPONENT_PACKAGES = (
    "backtest_analysis_decision_workspace",
    "backtest_analysis_result_workspace",
    "backtest_factor_readiness_panel",
    "backtest_handoff_action",
    "backtest_policy_signal_board",
    "backtest_price_freshness_preflight",
    "backtest_price_refresh_action",
    "backtest_workflow_shell",
    "final_review_investment_report",
    "practical_validation_data_action_board",
    "practical_validation_decision_workspace",
    "practical_validation_fix_queue",
)
PORTFOLIO_MONITORING_STATIC_ROOT = (
    REPO_ROOT / "app/web/streamlit_components/portfolio_monitoring_workbench/component_static"
)


def test_backtest_component_packages_use_component_static_contract() -> None:
    discovered_packages = {
        package_path.parent.parent.name
        for package_path in COMPONENT_ROOT.glob("*/frontend/package.json")
    }
    assert discovered_packages == set(BACKTEST_COMPONENT_PACKAGES)

    for component_name in BACKTEST_COMPONENT_PACKAGES:
        component_root = COMPONENT_ROOT / component_name
        vite_source = (component_root / "frontend/vite.config.ts").read_text(
            encoding="utf-8"
        )
        wrapper_source = (component_root / "component.py").read_text(
            encoding="utf-8"
        )

        assert 'outDir: "component_static"' in vite_source, component_name
        assert "emptyOutDir: true" in vite_source, component_name
        assert '/ "component_static"' in wrapper_source, component_name
        assert '/ "index.html"' in wrapper_source, component_name
        assert '/ "build"' not in wrapper_source, component_name


def test_backtest_component_static_entries_reference_existing_assets() -> None:
    for component_name in BACKTEST_COMPONENT_PACKAGES:
        static_root = COMPONENT_ROOT / component_name / "frontend/component_static"
        entry_path = static_root / "index.html"

        assert entry_path.is_file(), component_name
        entry_source = entry_path.read_text(encoding="utf-8")
        assert 'src="/assets/' not in entry_source, component_name
        assert 'href="/assets/' not in entry_source, component_name

        references = re.findall(
            r'(?:src|href)="\./([^"?#]+)',
            entry_source,
        )
        assert references, component_name
        for reference in references:
            assert (static_root / reference).is_file(), (
                f"{component_name}: missing {reference}"
            )


def test_backtest_component_static_entries_and_assets_are_git_tracked() -> None:
    tracked_result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
    )
    tracked_paths = {
        path
        for path in tracked_result.stdout.decode("utf-8").split("\0")
        if path
    }

    assert not any("/frontend/build/" in path for path in tracked_paths)
    for component_name in BACKTEST_COMPONENT_PACKAGES:
        static_root = COMPONENT_ROOT / component_name / "frontend/component_static"
        entry_path = static_root / "index.html"
        entry_relative = entry_path.relative_to(REPO_ROOT).as_posix()
        assert entry_relative in tracked_paths, component_name

        entry_source = entry_path.read_text(encoding="utf-8")
        references = re.findall(
            r'(?:src|href)="\./([^"?#]+)',
            entry_source,
        )
        for reference in references:
            asset_relative = (
                (static_root / reference).relative_to(REPO_ROOT).as_posix()
            )
            assert asset_relative in tracked_paths, (
                f"{component_name}: untracked {reference}"
            )


def test_portfolio_monitoring_component_static_entry_references_existing_relative_assets() -> None:
    entry_path = PORTFOLIO_MONITORING_STATIC_ROOT / "index.html"
    assert entry_path.is_file()
    entry_source = entry_path.read_text(encoding="utf-8")
    assert 'src="/assets/' not in entry_source
    assert 'href="/assets/' not in entry_source
    references = re.findall(r'(?:src|href)="\./([^"?#]+)', entry_source)
    assert references
    for reference in references:
        assert (PORTFOLIO_MONITORING_STATIC_ROOT / reference).is_file(), reference
