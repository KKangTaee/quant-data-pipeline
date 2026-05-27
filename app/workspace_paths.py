from __future__ import annotations

from pathlib import Path


def _find_project_root(start: Path | None = None) -> Path:
    """Locate the active worktree root from any app module path."""
    current = (start or Path(__file__).resolve()).resolve()
    search_root = current if current.is_dir() else current.parent
    for candidate in (search_root, *search_root.parents):
        if (candidate / ".aiworkspace" / "note" / "finance").exists():
            return candidate
        if (
            (candidate / "pyproject.toml").exists()
            and (candidate / "app").exists()
            and (candidate / "finance").exists()
        ):
            return candidate
    return Path(__file__).resolve().parents[1]


PROJECT_ROOT = _find_project_root()
FINANCE_NOTE_DIR = PROJECT_ROOT / ".aiworkspace" / "note" / "finance"
REGISTRIES_DIR = FINANCE_NOTE_DIR / "registries"
SAVED_DIR = FINANCE_NOTE_DIR / "saved"
RUN_HISTORY_DIR = FINANCE_NOTE_DIR / "run_history"
RUN_ARTIFACT_DIR = FINANCE_NOTE_DIR / "run_artifacts"
BACKTEST_ARTIFACT_DIR = FINANCE_NOTE_DIR / "backtest_artifacts"
FINANCE_DOCS_DIR = FINANCE_NOTE_DIR / "docs"
FINANCE_DATA_DOCS_DIR = FINANCE_DOCS_DIR / "data"
GLOSSARY_DOC_PATH = FINANCE_DOCS_DIR / "GLOSSARY.md"
PRACTICAL_VALIDATION_STRESS_WINDOW_FILE = (
    FINANCE_DATA_DOCS_DIR / "practical_validation_stress_windows_v1.json"
)
