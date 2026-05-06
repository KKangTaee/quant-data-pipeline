from __future__ import annotations

from datetime import datetime
from html import escape
from pathlib import Path
from typing import Any, Callable

import pandas as pd
import streamlit as st

from app.jobs.result_artifacts import RUN_ARTIFACT_DIR
from app.jobs.run_history import HISTORY_FILE, load_run_history
from app.web.backtest_ui_components import render_badge_strip, render_status_card_grid


def _status_tone(status: str | None) -> str:
    normalized = str(status or "").lower()
    if normalized == "success":
        return "positive"
    if normalized in {"partial_success", "warning", "review_required"}:
        return "warning"
    if normalized in {"failed", "failure", "error"} or "fail" in normalized:
        return "danger"
    return "neutral"


def _priority_tone(priority: str) -> str:
    if priority == "High":
        return "danger"
    if priority == "Medium":
        return "warning"
    return "neutral"


def _recent_files(directory: Path, pattern: str, limit: int = 5) -> list[Path]:
    if not directory.exists():
        return []
    return sorted(directory.glob(pattern), key=lambda path: path.stat().st_mtime, reverse=True)[:limit]


def _read_tail(path: Path, max_lines: int = 20) -> str:
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception as exc:
        return f"Failed to read file: {exc}"
    if not lines:
        return "(empty file)"
    return "\n".join(lines[-max_lines:])


def _artifact_paths(record: dict[str, Any]) -> dict[str, str]:
    details = dict(record.get("details") or {})
    artifact_info = dict(details.get("result_artifacts") or {})
    return {
        key: str(value)
        for key, value in artifact_info.items()
        if key in {"artifact_dir", "result_json", "manifest_json", "failure_csv"} and value
    }


def _path_exists(path_text: str) -> bool:
    try:
        return Path(path_text).exists()
    except (OSError, TypeError, ValueError):
        return False


def _missing_artifact_count(history: list[dict[str, Any]]) -> int:
    missing = 0
    for record in history[:10]:
        for path_text in _artifact_paths(record).values():
            if path_text and not _path_exists(path_text):
                missing += 1
    return missing


def _build_history_rows(history: list[dict[str, Any]]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for item in history:
        run_metadata = item.get("run_metadata") or {}
        rows.append(
            {
                "Started": item.get("started_at"),
                "Job": item.get("job_name"),
                "Status": item.get("status"),
                "Mode": run_metadata.get("execution_mode"),
                "Pipeline": run_metadata.get("pipeline_type"),
                "Symbols": item.get("symbols_requested"),
                "Failed": len(item.get("failed_symbols") or []),
                "Rows": item.get("rows_written"),
                "Duration": item.get("duration_sec"),
            }
        )
    return pd.DataFrame(rows)


def _history_label(record: dict[str, Any]) -> str:
    return f"{record.get('started_at') or '-'} | {record.get('job_name') or '-'} | {record.get('status') or '-'}"


def _status_counts(history: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"success": 0, "partial_success": 0, "failed": 0, "other": 0}
    for record in history:
        status = str(record.get("status") or "").lower()
        if status in counts:
            counts[status] += 1
        elif "fail" in status or status == "error":
            counts["failed"] += 1
        else:
            counts["other"] += 1
    return counts


def _build_action_items(
    *,
    running_job: dict[str, Any] | None,
    history: list[dict[str, Any]],
    failure_files: list[Path],
    missing_artifacts: int,
) -> list[dict[str, str]]:
    actions: list[dict[str, str]] = []
    if running_job:
        symbol_count = len(running_job.get("params", {}).get("symbols", []) or [])
        suffix = f" Target symbols: {symbol_count}." if symbol_count else ""
        actions.append(
            {
                "priority": "Medium",
                "title": "실행 중인 작업 확인",
                "detail": f"`{running_job.get('job_name')}`가 아직 실행 중입니다.{suffix}",
                "next": "작업이 끝날 때까지 Ingestion 실행 버튼은 잠시 멈춥니다.",
            }
        )

    if not history:
        actions.append(
            {
                "priority": "High",
                "title": "저장된 웹앱 실행 기록 없음",
                "detail": "운영 상태를 판단할 persistent run history가 아직 없습니다.",
                "next": "Ingestion에서 daily update 또는 metadata refresh를 한 번 실행합니다.",
            }
        )
        return actions

    latest = history[0]
    latest_status = str(latest.get("status") or "").lower()
    if latest_status != "success":
        actions.append(
            {
                "priority": "High" if "fail" in latest_status or latest_status == "error" else "Medium",
                "title": "최근 실행 결과 확인 필요",
                "detail": f"`{latest.get('job_name')}` latest status is `{latest.get('status')}`.",
                "next": "Run Health에서 선택 run의 실패 심볼, artifact, message를 확인합니다.",
            }
        )

    failed_count = sum(
        1 for record in history[:10] if _status_tone(str(record.get("status") or "")) == "danger"
    )
    partial_count = sum(
        1 for record in history[:10] if str(record.get("status") or "").lower() == "partial_success"
    )
    if failed_count or partial_count >= 2:
        actions.append(
            {
                "priority": "Medium",
                "title": "반복되는 실패 / 부분 성공 점검",
                "detail": f"최근 10개 run 중 failed {failed_count}개, partial {partial_count}개입니다.",
                "next": "Failure CSV와 Related Logs에서 같은 symbol/provider가 반복되는지 확인합니다.",
            }
        )

    if failure_files:
        actions.append(
            {
                "priority": "Medium",
                "title": "Failure CSV 검토",
                "detail": f"최근 failure artifact {len(failure_files)}개가 있습니다.",
                "next": "Logs & Artifacts에서 최신 failure CSV를 열어 symbol별 원인을 확인합니다.",
            }
        )

    if missing_artifacts:
        actions.append(
            {
                "priority": "Medium",
                "title": "Artifact 경로 확인",
                "detail": f"최근 history에서 현재 worktree에 없는 artifact path {missing_artifacts}개를 발견했습니다.",
                "next": "다른 worktree의 절대경로인지 확인하고, 필요한 경우 현재 worktree에서 run을 다시 남깁니다.",
            }
        )

    return actions


def _render_triage_flow(
    *,
    running_job: dict[str, Any] | None,
    latest: dict[str, Any] | None,
    actions: list[dict[str, str]],
    failure_files: list[Path],
) -> None:
    latest_status = str((latest or {}).get("status") or "No history")
    latest_job = str((latest or {}).get("job_name") or "persistent run 없음")
    steps = [
        {
            "number": "1",
            "title": "Monitor",
            "value": running_job.get("job_name") if running_job else "Idle",
            "detail": "실행 중인 ingestion job" if running_job else "현재 실행 중인 job 없음",
            "tone": "warning" if running_job else "positive",
        },
        {
            "number": "2",
            "title": "Triage",
            "value": latest_status,
            "detail": latest_job,
            "tone": _status_tone(latest_status),
        },
        {
            "number": "3",
            "title": "Inspect",
            "value": f"{len(actions)} action",
            "detail": "우선 확인할 run / artifact / log",
            "tone": "warning" if actions else "positive",
        },
        {
            "number": "4",
            "title": "Evidence",
            "value": f"{len(failure_files)} CSV",
            "detail": "failure CSV와 related log 확인",
            "tone": "warning" if failure_files else "neutral",
        },
        {
            "number": "5",
            "title": "Route",
            "value": "Next screen",
            "detail": "실행은 Ingestion, 재현은 History / Library",
            "tone": "neutral",
        },
    ]
    cards = []
    for step in steps:
        number = escape(str(step["number"]))
        title = escape(str(step["title"]))
        value = escape(str(step["value"]))
        detail = escape(str(step["detail"]))
        tone = escape(str(step["tone"]))
        cards.append(
            f'<div class="ops-triage-step ops-triage-step-{tone}">'
            f'<div class="ops-triage-number">{number}</div>'
            f'<div class="ops-triage-title">{title}</div>'
            f'<div class="ops-triage-value">{value}</div>'
            f'<div class="ops-triage-detail">{detail}</div>'
            "</div>"
        )
    st.markdown(
        """
        <style>
          .ops-triage-flow {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(152px, 1fr));
            gap: 0.6rem;
            margin: 0.35rem 0 1rem 0;
          }
          .ops-triage-step {
            min-height: 132px;
            padding: 0.82rem 0.85rem;
            border: 1px solid rgba(49, 51, 63, 0.14);
            border-radius: 8px;
            background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.06);
          }
          .ops-triage-step-positive { border-top: 4px solid #0f766e; }
          .ops-triage-step-warning { border-top: 4px solid #b45309; }
          .ops-triage-step-danger { border-top: 4px solid #b91c1c; }
          .ops-triage-step-neutral { border-top: 4px solid #475569; }
          .ops-triage-number {
            width: 1.55rem;
            height: 1.55rem;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 999px;
            background: #334155;
            color: #ffffff;
            font-size: 0.78rem;
            font-weight: 820;
            margin-bottom: 0.5rem;
          }
          .ops-triage-step-positive .ops-triage-number { background: #0f766e; }
          .ops-triage-step-warning .ops-triage-number { background: #b45309; }
          .ops-triage-step-danger .ops-triage-number { background: #b91c1c; }
          .ops-triage-title {
            color: #64748b;
            font-size: 0.78rem;
            font-weight: 820;
            text-transform: uppercase;
            letter-spacing: 0;
          }
          .ops-triage-value {
            margin-top: 0.25rem;
            color: #111827;
            font-size: 1.05rem;
            font-weight: 780;
            line-height: 1.24;
            overflow-wrap: anywhere;
          }
          .ops-triage-detail {
            margin-top: 0.35rem;
            color: #475569;
            font-size: 0.82rem;
            line-height: 1.32;
            overflow-wrap: anywhere;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(f'<div class="ops-triage-flow">{"".join(cards)}</div>', unsafe_allow_html=True)


def _render_action_inbox(actions: list[dict[str, str]]) -> None:
    st.markdown("### Action Inbox")
    st.caption("최근 실행 / artifact / 로그 기준으로 지금 먼저 볼 항목입니다.")
    if not actions:
        st.success("현재 우선 조치가 필요한 운영 이슈가 없습니다.")
        return

    for action in actions:
        with st.container(border=True):
            render_badge_strip(
                [
                    {
                        "label": "Priority",
                        "value": action["priority"],
                        "tone": _priority_tone(action["priority"]),
                    },
                    {"label": "Next", "value": action["next"], "tone": "neutral"},
                ]
            )
            st.markdown(f"**{action['title']}**")
            st.caption(action["detail"])


def _render_selected_run(record: dict[str, Any], log_dir: Path) -> None:
    status = str(record.get("status") or "-")
    run_metadata = record.get("run_metadata") or {}
    render_status_card_grid(
        [
            {"title": "Status", "value": status, "tone": _status_tone(status)},
            {"title": "Job", "value": record.get("job_name") or "-", "tone": "neutral"},
            {
                "title": "Failed Symbols",
                "value": len(record.get("failed_symbols") or []),
                "tone": "warning" if record.get("failed_symbols") else "positive",
            },
            {"title": "Duration Sec", "value": record.get("duration_sec") or "-", "tone": "neutral"},
        ]
    )
    st.caption(str(record.get("message") or ""))

    detail_tabs = st.tabs(["Inputs", "Steps / Details", "Artifacts", "Related Logs"])
    with detail_tabs[0]:
        st.json(
            {
                "execution_mode": run_metadata.get("execution_mode"),
                "pipeline_type": run_metadata.get("pipeline_type"),
                "symbol_source": run_metadata.get("symbol_source"),
                "symbol_count": run_metadata.get("symbol_count"),
                "input_params": run_metadata.get("input_params") or {},
                "runtime_marker": run_metadata.get("runtime_marker"),
                "git_sha": run_metadata.get("git_sha"),
            },
            expanded=False,
        )
    with detail_tabs[1]:
        details = record.get("details") or {}
        if details:
            st.json(details, expanded=False)
        else:
            st.info("이 run에는 details payload가 없습니다.")
    with detail_tabs[2]:
        paths = _artifact_paths(record)
        if not paths:
            st.info("이 run에는 result_artifacts 경로가 없습니다.")
        else:
            artifact_rows = [
                {"Artifact": key, "Path": value, "Exists Here": _path_exists(value)}
                for key, value in paths.items()
            ]
            st.dataframe(pd.DataFrame(artifact_rows), width="stretch", hide_index=True)
    with detail_tabs[3]:
        related_logs = _related_logs_for_job(log_dir, str(record.get("job_name") or ""))
        if not related_logs:
            st.info("현재 worktree의 logs/에서 관련 log 후보를 찾지 못했습니다.")
        else:
            selected_log = st.selectbox(
                "Related Log File",
                options=[path.name for path in related_logs],
                key=f"ops_review_related_log_{record.get('started_at')}_{record.get('job_name')}",
            )
            chosen = next(path for path in related_logs if path.name == selected_log)
            st.caption(f"Path: {chosen}")
            st.code(_read_tail(chosen), language="text")


def _related_logs_for_job(log_dir: Path, job_name: str, limit: int = 5) -> list[Path]:
    mapping = {
        "daily_market_update": ["*price*.log", "*ohlcv*.log"],
        "collect_ohlcv": ["*price*.log", "*ohlcv*.log"],
        "pipeline_core_market_data": ["*price*.log", "*fundamentals*.log", "*factors*.log"],
        "weekly_fundamental_refresh": ["*fundamentals*.log", "*factors*.log"],
        "collect_fundamentals": ["*fundamentals*.log"],
        "calculate_factors": ["*factors*.log"],
        "extended_statement_refresh": ["*financial_statements*.log", "*fundamentals*.log", "*factors*.log"],
        "collect_financial_statements": ["*financial_statements*.log"],
        "rebuild_statement_shadow": ["*fundamentals*.log", "*factors*.log"],
        "collect_asset_profiles": ["*profile*.log"],
        "metadata_refresh": ["*profile*.log"],
    }
    patterns = mapping.get(job_name, ["*.log"])
    seen: set[Path] = set()
    logs: list[Path] = []
    for pattern in patterns:
        for path in _recent_files(log_dir, pattern, limit=limit):
            if path in seen:
                continue
            seen.add(path)
            logs.append(path)
    return logs[:limit]


def _render_run_health(history: list[dict[str, Any]], log_dir: Path) -> None:
    st.markdown("### Run Health")
    st.caption("웹앱 ingestion / refresh / factor job의 persistent history를 run 단위로 점검합니다.")
    if not history:
        st.info(f"아직 persistent run history가 없습니다. 기본 경로: `{HISTORY_FILE}`")
        return

    counts = _status_counts(history)
    render_status_card_grid(
        [
            {"title": "Success", "value": counts["success"], "tone": "positive"},
            {"title": "Partial", "value": counts["partial_success"], "tone": "warning"},
            {"title": "Failed", "value": counts["failed"], "tone": "danger" if counts["failed"] else "neutral"},
            {"title": "History Rows", "value": len(history), "detail": str(HISTORY_FILE), "tone": "neutral"},
        ]
    )
    st.dataframe(_build_history_rows(history), width="stretch", hide_index=True)

    options = {_history_label(record): record for record in history}
    selected_label = st.selectbox("Inspect Run", options=list(options.keys()), key="ops_review_selected_run")
    _render_selected_run(options[selected_label], log_dir)


def _render_logs_and_artifacts(csv_dir: Path, log_dir: Path) -> None:
    st.markdown("### Logs & Artifacts")
    st.caption("기본은 선택 run을 먼저 보되, 전역 최신 failure CSV와 log도 여기서 빠르게 확인합니다.")
    tabs = st.tabs(["Failure CSV", "Recent Logs", "Artifact Index"])

    with tabs[0]:
        failure_files = _recent_files(csv_dir, "*failures*.csv", limit=5)
        if not failure_files:
            st.info("현재 worktree의 csv/에서 failure CSV를 찾지 못했습니다.")
        else:
            selected = st.selectbox("Failure CSV", options=[path.name for path in failure_files], key="ops_failure_csv")
            path = next(item for item in failure_files if item.name == selected)
            st.caption(f"Path: {path}")
            try:
                df = pd.read_csv(path)
            except Exception as exc:
                st.error(f"Failure CSV를 읽지 못했습니다: {exc}")
            else:
                if df.empty:
                    st.info("선택한 failure CSV는 비어 있습니다.")
                else:
                    st.dataframe(df.head(30), width="stretch", hide_index=True)

    with tabs[1]:
        log_files = _recent_files(log_dir, "*.log", limit=5)
        if not log_files:
            st.info("현재 worktree의 logs/에서 log 파일을 찾지 못했습니다.")
        else:
            selected = st.selectbox("Recent Log", options=[path.name for path in log_files], key="ops_recent_log")
            path = next(item for item in log_files if item.name == selected)
            st.caption(f"Path: {path}")
            st.code(_read_tail(path), language="text")

    with tabs[2]:
        artifact_dirs = _recent_files(RUN_ARTIFACT_DIR, "*", limit=10)
        artifact_dirs = [path for path in artifact_dirs if path.is_dir()]
        if not artifact_dirs:
            st.info(f"현재 worktree에 run artifact directory가 없습니다. 기본 경로: `{RUN_ARTIFACT_DIR}`")
        else:
            rows = []
            for path in artifact_dirs:
                rows.append(
                    {
                        "Artifact Key": path.name,
                        "Result JSON": (path / "result.json").exists(),
                        "Manifest": (path / "manifest.json").exists(),
                        "Path": str(path),
                    }
                )
            st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)


def _render_route_guidance() -> None:
    st.markdown("### Where To Go Next")
    st.caption("Ops Review는 문제를 찾는 화면입니다. 실행, 재현, 후보 검토는 각 전용 화면에서 처리합니다.")
    rows = [
        {
            "Need": "데이터 수집 / 재실행",
            "Go To": "Workspace > Ingestion",
            "Boundary": "Ops Review에서 직접 job을 실행하지 않습니다.",
        },
        {
            "Need": "백테스트 run 재현 / form 복원",
            "Go To": "Operations > Backtest Run History",
            "Boundary": "Backtest replay action은 Backtest Run History가 담당합니다.",
        },
        {
            "Need": "저장 후보 재검토 / result curve rebuild",
            "Go To": "Operations > Candidate Library",
            "Boundary": "후보 replay는 Candidate Library가 담당합니다.",
        },
        {
            "Need": "포트폴리오 workflow 의미 확인",
            "Go To": "Reference > Guides",
            "Boundary": "Guide는 decision flow reference입니다.",
        },
    ]
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)


def render_operations_dashboard(
    *,
    runtime_marker: str,
    loaded_at: datetime,
    git_sha: str | None,
    running_job: dict[str, Any] | None,
    recent_results: list[dict[str, Any]],
    log_dir: Path,
    csv_dir: Path,
    render_runtime_snapshot: Callable[[], None] | None = None,
) -> None:
    """Render the Operations-owned run health and artifact review dashboard."""

    history = load_run_history(limit=30)
    failure_files = _recent_files(csv_dir, "*failures*.csv", limit=5)
    missing_artifacts = _missing_artifact_count(history)
    latest = history[0] if history else None
    latest_status = str((latest or {}).get("status") or "-")
    actions = _build_action_items(
        running_job=running_job,
        history=history,
        failure_files=failure_files,
        missing_artifacts=missing_artifacts,
    )

    st.title("Operations Dashboard")
    st.caption(
        "웹앱 실행 기록, failure artifact, log, runtime 상태를 운영 관점에서 점검합니다. "
        "후보 replay나 백테스트 재실행은 전용 Operations 화면으로 분리합니다."
    )
    _render_triage_flow(
        running_job=running_job,
        latest=latest,
        actions=actions,
        failure_files=failure_files,
    )

    render_status_card_grid(
        [
            {
                "title": "Running Job",
                "value": running_job.get("job_name") if running_job else "Idle",
                "detail": "현재 실행 중" if running_job else "실행 대기",
                "tone": "warning" if running_job else "positive",
            },
            {
                "title": "Latest Persisted Run",
                "value": latest_status,
                "detail": (latest or {}).get("job_name") or "No history",
                "tone": _status_tone(latest_status),
            },
            {
                "title": "Action Items",
                "value": len(actions),
                "detail": "우선 확인할 운영 이슈",
                "tone": "warning" if actions else "positive",
            },
            {
                "title": "Failure CSV",
                "value": len(failure_files),
                "detail": "최근 failure artifact",
                "tone": "warning" if failure_files else "positive",
            },
            {
                "title": "Runtime",
                "value": git_sha or "unknown",
                "detail": runtime_marker,
                "tone": "neutral",
            },
        ]
    )

    if recent_results:
        latest_session = recent_results[0]
        with st.expander("Session Latest Run", expanded=False):
            render_badge_strip(
                [
                    {"label": "Job", "value": latest_session.get("job_name") or "-", "tone": "neutral"},
                    {
                        "label": "Status",
                        "value": latest_session.get("status") or "-",
                        "tone": _status_tone(str(latest_session.get("status") or "")),
                    },
                    {"label": "Finished", "value": latest_session.get("finished_at") or "-", "tone": "neutral"},
                ]
            )
            st.caption(str(latest_session.get("message") or ""))

    _render_action_inbox(actions)
    _render_run_health(history, log_dir)
    _render_logs_and_artifacts(csv_dir, log_dir)
    _render_route_guidance()

    with st.expander("System Snapshot", expanded=False):
        if render_runtime_snapshot is not None:
            render_runtime_snapshot()
        else:
            render_status_card_grid(
                [
                    {"title": "Runtime Marker", "value": runtime_marker, "tone": "neutral"},
                    {"title": "Loaded At", "value": loaded_at.strftime("%Y-%m-%d %H:%M:%S"), "tone": "neutral"},
                    {"title": "Git SHA", "value": git_sha or "unknown", "tone": "neutral"},
                ]
            )
