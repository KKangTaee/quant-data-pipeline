from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv

from app.workspace_paths import PROJECT_ROOT


def load_project_local_env(project_root: Path | None = None) -> bool:
    """Load the active worktree's local environment without overriding process values."""
    root = Path(project_root) if project_root is not None else PROJECT_ROOT
    env_path = root / ".env"
    if not env_path.is_file():
        return False
    return bool(load_dotenv(dotenv_path=env_path, override=False))
