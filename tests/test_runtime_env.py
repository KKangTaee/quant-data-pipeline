from __future__ import annotations

import os
from pathlib import Path


def test_load_project_local_env_reads_root_file(
    tmp_path: Path, monkeypatch
) -> None:
    from app.runtime_env import load_project_local_env

    monkeypatch.delenv("FRED_API_KEY", raising=False)
    (tmp_path / ".env").write_text("FRED_API_KEY=" + "from-local-file\n")

    assert load_project_local_env(tmp_path) is True
    assert os.environ["FRED_API_KEY"] == "from-local-file"


def test_load_project_local_env_preserves_process_value(
    tmp_path: Path, monkeypatch
) -> None:
    from app.runtime_env import load_project_local_env

    monkeypatch.setenv("FRED_API_KEY", "from-process")
    (tmp_path / ".env").write_text("FRED_API_KEY=" + "from-local-file\n")

    assert load_project_local_env(tmp_path) is True
    assert os.environ["FRED_API_KEY"] == "from-process"


def test_load_project_local_env_missing_file_is_harmless(
    tmp_path: Path, monkeypatch
) -> None:
    from app.runtime_env import load_project_local_env

    monkeypatch.delenv("FRED_API_KEY", raising=False)

    assert load_project_local_env(tmp_path) is False
    assert "FRED_API_KEY" not in os.environ
