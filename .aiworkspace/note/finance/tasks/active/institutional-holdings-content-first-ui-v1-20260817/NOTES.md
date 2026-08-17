# Institutional Holdings Content-First UI V1 Notes

## Decisions

- 2026-08-17: 사용자는 `Market Research + Today` content-first 하이브리드 A안을 선택했다.
- 2026-08-17: selected state는 full-height left line 대신 text contrast, subtle tint와 short
  bottom underline을 사용한다.
- 2026-08-17: manager 선택은 검색 query보다 높은 우선순위를 가지며 성공한 선택 뒤 query를
  초기화한다.
- 2026-08-17: page entry는 local-only due check를 유지하고 SEC 요청은 explicit click 이후만
  수행한다.

## Discovery

- `select_manager`는 selected CIK을 저장하지만 manager search query를 비우지 않는다.
- `_resolve_selected_manager(..., search_active=True)`는 selected CIK이 query match가 아니면
  첫 query match를 다시 반환한다.
- `.ip-studio-rail .ip-manager-tab--active`의 full-height inset shadow가 사용자가 지적한
  늘어나는 좌측 선택선이다.
