from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from decimal import Decimal
from typing import Any, Callable
from collections.abc import Mapping
from uuid import uuid4

from .persistence import (
    DEFAULT_PORTFOLIO_GROUP_ID,
    DEFAULT_PORTFOLIO_GROUP_NAME,
    MonitoringItemRecord,
    MonitoringRepository,
    PortfolioGroupRecord,
    StoredCommandRecord,
)
from .schemas import (
    AddMonitoringItemInput,
    CommandStatus,
    CommandType,
    MonitoringCommandInput,
    build_request_fingerprint,
    validate_add_item_input,
)


ACTIVE_ITEM_STATUSES = {"active", "data_review"}
MAX_ACTIVE_ITEMS_PER_GROUP = 10


class CommandValidationError(ValueError):
    pass


class CommandConflictError(RuntimeError):
    pass


@dataclass(frozen=True)
class EntryResolution:
    effective_start_date: date
    entry_close: Decimal
    initial_capital: Decimal
    metadata: dict[str, Any] | None = None
    status: str = "active"


@dataclass(frozen=True)
class EndResolution:
    requested_end_date: date
    effective_end_date: date
    exit_value: Decimal


@dataclass(frozen=True)
class CommandResult:
    status: CommandStatus
    command_id: str
    target_id: str
    replayed: bool
    message: str


def _clean_name(value: Any) -> str:
    name = str(value or "").strip()
    if not name:
        raise CommandValidationError("Portfolio name is required.")
    return name


def _assert_command_type(command: MonitoringCommandInput, expected: CommandType) -> None:
    if command.command_type != expected:
        raise CommandValidationError(f"Expected {expected.value} command.")
    if not str(command.command_id or "").strip():
        raise CommandValidationError("command_id is required.")


def _command_fingerprint(command: MonitoringCommandInput, semantic_payload: dict[str, Any]) -> str:
    return build_request_fingerprint(
        {
            "command_type": command.command_type,
            "target_id": command.target_id,
            "payload": semantic_payload,
        }
    )


def _result_payload(result: CommandResult) -> dict[str, Any]:
    payload = asdict(result)
    payload["status"] = result.status.value
    return payload


def _replay_result(record: StoredCommandRecord, fingerprint: str) -> CommandResult | None:
    if record.request_fingerprint != fingerprint:
        raise CommandConflictError("The same command_id was used for a different request.")
    if record.status == CommandStatus.PENDING:
        raise CommandConflictError("The command is already pending.")
    payload = dict(record.result_json or {})
    if not payload or not record.result_ref:
        raise CommandConflictError("The stored command result is unavailable.")
    return CommandResult(
        status=CommandStatus(str(payload.get("status") or record.status.value)),
        command_id=record.command_id,
        target_id=str(payload.get("target_id") or record.result_ref),
        replayed=True,
        message=str(payload.get("message") or "Command result replayed."),
    )


def _existing_result(
    repository: MonitoringRepository,
    command_id: str,
    fingerprint: str,
) -> CommandResult | None:
    existing = repository.get_command(command_id)
    return _replay_result(existing, fingerprint) if existing is not None else None


def _execute(
    repository: MonitoringRepository,
    command: MonitoringCommandInput,
    fingerprint: str,
    mutate: Callable[[], CommandResult],
) -> CommandResult:
    replay = _existing_result(repository, command.command_id, fingerprint)
    if replay is not None:
        return replay
    with repository.transaction():
        replay = _existing_result(repository, command.command_id, fingerprint)
        if replay is not None:
            return replay
        repository.insert_command(
            StoredCommandRecord(
                command_id=command.command_id,
                command_type=command.command_type.value,
                target_id=command.target_id,
                request_fingerprint=fingerprint,
                status=CommandStatus.PENDING,
            )
        )
        result = mutate()
        repository.finish_command(
            command.command_id,
            status=CommandStatus.SUCCEEDED,
            result_ref=result.target_id,
            result_json=_result_payload(result),
        )
        return result


def ensure_default_group(repository: MonitoringRepository) -> PortfolioGroupRecord:
    """Create the deterministic default group once without relying on UI state."""

    repository_method = getattr(repository, "get_or_create_default_group", None)
    if callable(repository_method):
        return repository_method()
    with repository.transaction():
        current = repository.get_group(DEFAULT_PORTFOLIO_GROUP_ID, for_update=True)
        if current is not None:
            return current
        existing_default = next(
            (group for group in repository.list_groups() if group.is_default),
            None,
        )
        if existing_default is not None:
            return existing_default
        return repository.insert_group(
            PortfolioGroupRecord(
                portfolio_group_id=DEFAULT_PORTFOLIO_GROUP_ID,
                name=DEFAULT_PORTFOLIO_GROUP_NAME,
                is_default=True,
            )
        )


def execute_create_group(
    repository: MonitoringRepository,
    command: MonitoringCommandInput,
) -> CommandResult:
    _assert_command_type(command, CommandType.CREATE_GROUP)
    name = _clean_name(command.payload.get("name"))
    raw_metadata = command.payload.get("metadata")
    if raw_metadata is not None and not isinstance(raw_metadata, Mapping):
        raise CommandValidationError("Portfolio group metadata must be an object.")
    metadata = dict(raw_metadata or {})
    fingerprint = _command_fingerprint(command, {"name": name, "metadata": metadata})

    def mutate() -> CommandResult:
        if any(group.name.casefold() == name.casefold() for group in repository.list_groups()):
            raise CommandValidationError("A portfolio group with this name already exists.")
        group_id = f"monitoring_group_{uuid4().hex[:16]}"
        repository.insert_group(
            PortfolioGroupRecord(
                portfolio_group_id=group_id,
                name=name,
                is_default=False,
                metadata=metadata,
            )
        )
        return CommandResult(
            status=CommandStatus.SUCCEEDED,
            command_id=command.command_id,
            target_id=group_id,
            replayed=False,
            message="Portfolio group created.",
        )

    return _execute(repository, command, fingerprint, mutate)


def execute_rename_group(
    repository: MonitoringRepository,
    command: MonitoringCommandInput,
) -> CommandResult:
    _assert_command_type(command, CommandType.RENAME_GROUP)
    group_id = str(command.target_id or "").strip()
    if not group_id:
        raise CommandValidationError("portfolio_group_id is required.")
    if command.expected_version is None or command.expected_version < 1:
        raise CommandValidationError("expected_version is required.")
    name = _clean_name(command.payload.get("name"))
    fingerprint = _command_fingerprint(
        command,
        {"name": name, "expected_version": command.expected_version},
    )

    def mutate() -> CommandResult:
        current = repository.get_group(group_id, for_update=True)
        if current is None:
            raise CommandValidationError("Portfolio group not found.")
        if any(
            group.portfolio_group_id != group_id
            and group.name.casefold() == name.casefold()
            for group in repository.list_groups()
        ):
            raise CommandValidationError("A portfolio group with this name already exists.")
        updated = repository.update_group_name(group_id, name, command.expected_version or 0)
        if updated is None:
            raise CommandConflictError("Portfolio group version conflict.")
        return CommandResult(
            status=CommandStatus.SUCCEEDED,
            command_id=command.command_id,
            target_id=group_id,
            replayed=False,
            message="Portfolio group renamed.",
        )

    return _execute(repository, command, fingerprint, mutate)


def _validated_entry(entry: EntryResolution, requested_start_date: date) -> EntryResolution:
    if entry.effective_start_date < requested_start_date:
        raise CommandValidationError("effective start date cannot precede the requested date.")
    if entry.entry_close <= 0:
        raise CommandValidationError("entry close must be positive.")
    if entry.initial_capital <= 0:
        raise CommandValidationError("initial capital must be positive.")
    if entry.status not in ACTIVE_ITEM_STATUSES:
        raise CommandValidationError("unsupported initial item status.")
    return entry


def execute_add_item(
    repository: MonitoringRepository,
    command: MonitoringCommandInput,
    item: AddMonitoringItemInput,
    *,
    resolve_entry: Callable[[AddMonitoringItemInput], EntryResolution],
) -> CommandResult:
    _assert_command_type(command, CommandType.ADD_ITEM)
    validated = validate_add_item_input(item)
    semantic_payload = asdict(validated)
    fingerprint = _command_fingerprint(command, semantic_payload)
    replay = _existing_result(repository, command.command_id, fingerprint)
    if replay is not None:
        return replay
    entry = _validated_entry(resolve_entry(validated), validated.requested_start_date)

    def mutate() -> CommandResult:
        if repository.get_group(validated.portfolio_group_id, for_update=True) is None:
            raise CommandValidationError("Portfolio group not found.")
        active_items = repository.list_items(
            validated.portfolio_group_id,
            statuses=ACTIVE_ITEM_STATUSES,
        )
        if any(
            existing.source_type == validated.source_type.value
            and existing.source_ref.casefold() == validated.source_ref.casefold()
            for existing in active_items
        ):
            raise CommandValidationError("This source is already active in the portfolio group.")
        if len(active_items) >= MAX_ACTIVE_ITEMS_PER_GROUP:
            raise CommandValidationError("A portfolio group can contain a maximum 10 active items.")
        monitoring_item_id = f"monitoring_item_{uuid4().hex[:16]}"
        repository.insert_item(
            MonitoringItemRecord(
                monitoring_item_id=monitoring_item_id,
                portfolio_group_id=validated.portfolio_group_id,
                source_type=validated.source_type.value,
                source_ref=validated.source_ref,
                instrument_kind=validated.instrument_kind.value,
                requested_start_date=validated.requested_start_date,
                effective_start_date=entry.effective_start_date,
                funding_mode=validated.funding_mode.value,
                input_notional=validated.input_notional,
                input_shares=validated.input_shares,
                entry_close=entry.entry_close,
                initial_capital=entry.initial_capital,
                status=entry.status,
                metadata=dict(entry.metadata or {}),
            )
        )
        return CommandResult(
            status=CommandStatus.SUCCEEDED,
            command_id=command.command_id,
            target_id=monitoring_item_id,
            replayed=False,
            message="Monitoring item added.",
        )

    return _execute(repository, command, fingerprint, mutate)


def execute_end_item(
    repository: MonitoringRepository,
    command: MonitoringCommandInput,
    *,
    resolve_end: Callable[[MonitoringItemRecord], EndResolution],
) -> CommandResult:
    _assert_command_type(command, CommandType.END_ITEM)
    item_id = str(command.target_id or "").strip()
    if not item_id:
        raise CommandValidationError("monitoring_item_id is required.")
    fingerprint = _command_fingerprint(command, {"monitoring_item_id": item_id})
    replay = _existing_result(repository, command.command_id, fingerprint)
    if replay is not None:
        return replay
    current = repository.get_item(item_id)
    if current is None:
        raise CommandValidationError("Monitoring item not found.")
    if current.status not in ACTIVE_ITEM_STATUSES:
        raise CommandValidationError("Monitoring item is not active.")
    resolution = resolve_end(current)
    if resolution.effective_end_date < current.effective_start_date:
        raise CommandValidationError("effective end date cannot precede effective start date.")
    if resolution.exit_value < 0:
        raise CommandValidationError("exit value cannot be negative.")

    def mutate() -> CommandResult:
        locked = repository.get_item(item_id, for_update=True)
        if locked is None or locked.status not in ACTIVE_ITEM_STATUSES:
            raise CommandConflictError("Monitoring item status changed before tracking end.")
        ended = repository.end_item(item_id, resolution)
        if ended is None:
            raise CommandConflictError("Monitoring item could not be ended.")
        return CommandResult(
            status=CommandStatus.SUCCEEDED,
            command_id=command.command_id,
            target_id=item_id,
            replayed=False,
            message=(
                f"추적 종료 완료 · 요청일 {resolution.requested_end_date.isoformat()} · "
                f"적용일 {resolution.effective_end_date.isoformat()} · "
                f"종료금액 ${resolution.exit_value:,.2f}는 현금으로 유지됩니다."
            ),
        )

    return _execute(repository, command, fingerprint, mutate)


def execute_reopen_item(
    repository: MonitoringRepository,
    command: MonitoringCommandInput,
) -> CommandResult:
    """Cancel a tracking end while preserving the original monitoring contract."""

    _assert_command_type(command, CommandType.REOPEN_ITEM)
    item_id = str(command.target_id or "").strip()
    if not item_id:
        raise CommandValidationError("monitoring_item_id is required.")
    fingerprint = _command_fingerprint(command, {"monitoring_item_id": item_id})
    replay = _existing_result(repository, command.command_id, fingerprint)
    if replay is not None:
        return replay
    current = repository.get_item(item_id)
    if current is None:
        raise CommandValidationError("Monitoring item not found.")
    if current.status != "ended":
        raise CommandValidationError("Only an ended monitoring item can be reopened.")

    def mutate() -> CommandResult:
        locked = repository.get_item(item_id, for_update=True)
        if locked is None or locked.status != "ended":
            raise CommandConflictError("Monitoring item status changed before tracking end cancellation.")
        if repository.get_group(locked.portfolio_group_id, for_update=True) is None:
            raise CommandValidationError("Portfolio group not found.")
        active_items = repository.list_items(
            locked.portfolio_group_id,
            statuses=ACTIVE_ITEM_STATUSES,
        )
        if any(
            existing.source_type == locked.source_type
            and existing.source_ref.casefold() == locked.source_ref.casefold()
            for existing in active_items
        ):
            raise CommandValidationError("This source is already active in the portfolio group.")
        if len(active_items) >= MAX_ACTIVE_ITEMS_PER_GROUP:
            raise CommandValidationError("A portfolio group can contain a maximum of 10 active items.")
        reopened = repository.reopen_item(item_id)
        if reopened is None:
            raise CommandConflictError("Monitoring item could not be reopened.")
        return CommandResult(
            status=CommandStatus.SUCCEEDED,
            command_id=command.command_id,
            target_id=item_id,
            replayed=False,
            message="추적 종료를 취소했습니다. 기존 시작일과 보유 계약으로 계속 추적합니다.",
        )

    return _execute(repository, command, fingerprint, mutate)
