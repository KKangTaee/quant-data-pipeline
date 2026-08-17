# Plan

## Goal

Root `README.md`와 Reference Center catalog가 2026-08-17 기준 Finance Console surface와 Market Research 3-family / 8-view 구조를 정확히 안내하도록 최신화한다.

## 이걸 하는 이유?

README는 새 사용자와 AI 작업자의 첫 진입점이고, Reference Center는 제품 내부 도움말의 source contract다. 직전 문서 정리에서 durable docs는 최신화했지만, README와 Reference catalog가 current view를 덜 구체적으로 말하면 다음 작업자가 오래된 탭 구조로 다시 사고할 수 있다.

## Scope

- `README.md`
- `app/services/reference_center.py`
- `tests/test_reference_center.py`
- 이 task 기록

## Out Of Scope

- React UI layout 변경
- route key, URL, module, saved JSONL rename
- registry / saved / run history 수정
- Browser QA가 필요한 화면 시각 변경

## Stop Condition

- README가 current navigation과 Market Research / Data Operations 흐름을 정확히 설명한다.
- Reference Center catalog가 current Market Research 주요 view를 검색 가능한 항목으로 포함한다.
- focused compile / Reference Center contract / stale-label / diff checks를 통과한다.
