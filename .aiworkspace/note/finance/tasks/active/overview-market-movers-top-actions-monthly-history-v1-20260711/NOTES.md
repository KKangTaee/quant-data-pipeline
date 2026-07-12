# Notes

- 2026-07-11 17:12 run은 S&P 500 Monthly에서 FDXF/HONA 2개를 1y window로 다시 수집했고 성공했지만 각각 31/1 rows만 저장됐다.
- 기존 preflight는 `row_count < 45`를 `insufficient_window_rows -> missing_symbols`로 분류하므로 full-window 성공 여부와 무관하게 다음 화면에서도 같은 두 종목을 다시 수집 대상으로 만든다.
- 해결은 universe에서 제거하거나 synthetic backfill하는 것이 아니라, full-window 수집 후에도 남는 실제 짧은 이력을 별도 issue로 기록해 refreshable gap과 분리하는 것이다.
- 버튼 내부의 긴 `detail`은 제거하고 같은 정보의 compact summary를 action row 아래 보조 설명으로 낮춘다.
- `limited_price_history` issue가 active로 남아 있어도 현재 row count가 해당 period threshold를 충족하면 preflight는 issue보다 정상 계산 경로를 우선한다.
- Monthly Browser QA에서는 `가격 이력 갱신`을 숨기고 `유니버스 기준 갱신`, `화면 새로고침`만 유지했으며 FDXF/HONA 설명을 버튼 아래 한 줄로 표시했다.
