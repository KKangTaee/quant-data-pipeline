# Notes

- 기존 SVG point의 native `<title>`만으로는 사용자가 명확한 tooltip을 확인하기 어렵다.
- dense 시계열이므로 개별 3.4px point hover보다 plot-wide nearest-point 탐색이 적합하다.
- font 변경은 Portfolio Monitoring component 전용 stylesheet에만 적용한다.
- pointer와 keyboard focus는 동일한 `activeIndex`를 사용한다. tooltip은 chart right edge에서 왼쪽으로 전환하고 plot 상하 경계를 넘지 않는다.
- 기존 stylesheet의 모든 `font-size` 선언 안 px 값을 기계적으로 +1하고, 명시 크기가 없는 버튼/텍스트도 component base를 16px→17px로 고정했다. spacing, card size, 다른 React/Streamlit 탭은 변경하지 않았다.
- actual QA group은 392개 가치 관측치를 가졌고 focus 확인 지점에서 `3월 5일 · $12,585`, guide line, active point가 동시에 렌더링됐다.
