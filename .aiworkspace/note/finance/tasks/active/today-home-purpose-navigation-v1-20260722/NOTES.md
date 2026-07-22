# Notes

- 사용자 선택: B안 `브리프형 워크벤치`.
- 이전 비교 시안의 백색/단색은 구조 비교용이며 제품 구현은 기존 Market Context design language를 따른다.
- 대표 포트폴리오는 `monitoring_portfolio_group.is_default = 1` 계약을 재사용한다.
- actual default group은 5개 active item과 READY group value result를 반환한다.
- 초기 smoke에서는 Futures Macro materialized snapshot이 MISSING이었고, 최종 actual QA에서는 저장 snapshot이 READY로 갱신됐다. Economic Cycle LIMITED와 S&P provisional 때문에 Today 종합 상태는 계속 PARTIAL이다.
- V1의 종목 기여는 workspace가 제공하는 누적 contribution을 사용하며 화면에 `누적 기여`로 명시한다.
- Streamlit multipage에서 `default=True` page는 `url_path="today"`가 있어도 browser root `/`로 canonicalize된다. 사용자 요구인 최초 진입은 root에서 충족한다.
- 각 상세 renderer는 보존 범위다. 새 navigation label과 다른 legacy owner-path copy의 전면 교체는 별도 cleanup으로 분리한다.
- 대표 포트폴리오는 마지막 session 선택이 아니라 기존 `is_default` group으로 고정한다. Today loader는 default group을 자동 생성하지 않는다.
