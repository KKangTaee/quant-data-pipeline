# Notes

- 화면의 non-daily Market Movers는 `date_window.effective_end_date`를 기준으로 계산한다.
- 기존 action은 `_market_movers_today()`를 as-of로 사용해 KST 로컬 날짜가 DB 최신 EOD보다 하루 앞선 경우 current symbols를 stale로 분류할 수 있었다.
- 기존 Top1000/Top2000 action universe는 `asset_profile.market_cap` 기반 loader를 사용해 화면의 materialized liquidity universe와 어긋날 수 있었다.
- 기존 stale batch는 가장 오래된 stale start 하나로 묶어, 오래된 1개가 많은 최신 stale 종목의 수집 범위를 뒤로 끌 수 있었다.
- 변경 후 Top1000/Top2000 action universe는 `market_liquidity_universe_member`를 사용한다. 따라서 화면 ranking universe와 refresh universe가 맞는다.
- 변경 후 React path는 snapshot의 `date_window.effective_end_date`를 EOD refresh action의 `as_of_date`로 넘긴다. KST 로컬 날짜가 하루 앞서도 화면 기준 최신 EOD가 current로 분류된다.
- 보수적인 확장 자체는 없애지 않았다. Weekly / Monthly / Yearly 계산은 현재 return뿐 아니라 이전 구간, momentum delta, average dollar volume, relative / unusual volume baseline, sector breadth에 필요한 과거 row가 필요하다. 다만 이제 그 범위가 필요한 symbol batch에만 적용된다.
- `자료정상`은 화면 계산 정상만 뜻하지 않도록 React summary에서 `계산 가능 · 이력 보강 필요`로 분리했다.
