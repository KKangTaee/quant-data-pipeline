# Notes

- 적용 범위는 선택 direct security 가격 차트뿐이다.
- A안인 기존 SVG client-side viewport를 채택했다.
- mobile V1은 touch gesture 대신 explicit controls만 제공한다.
- 120-row DB projection과 line/candle price semantics는 변경하지 않는다.
- viewport는 inclusive `startIndex/endIndex`이며 line/candle mode 전환 동안 유지된다.
- 선택 item, row count 또는 first/last date가 바뀌면 stale viewport를 full range로 reset한다.
- wheel과 drag는 visible rows만 다시 그리며 Python rerun, DB read, provider fetch를 발생시키지 않는다.
- pointer cancel/lost-capture는 drag와 tooltip state를 함께 정리한다.
- 가독성 후속은 React markup, SVG viewBox와 data contract를 유지하고 component-local CSS만 변경한다.
- desktop `pm-content-grid`는 목록 `minmax(280px, .35fr)`, 선택 상세 `minmax(0, .65fr)`를 사용한다.
- 선택 가격 차트의 Y축 가격, `VOL`, X축 날짜는 11px/700과 더 진한 `#63798a`를 사용한다.
- 900px 이하는 기존 단일 열, 420px은 기존 explicit-controls-only 경계를 유지한다.
