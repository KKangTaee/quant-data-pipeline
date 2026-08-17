# Master Merge Resolution Notes

- merge base 이후 current branch는 Sentiment의 1W·1M 실제 관측 변화와 `3/4차 paused`
  상태를, master는 Futures Macro 장중 관측·결정형 UI·재가격화 레이더를 추가했다.
- `ROADMAP.md`의 충돌한 Market Research 한 줄은 독립된 두 제품 사실이므로 모두 보존한다.
- 최종 React root는 `ForecastValidationGate`를 렌더하지 않고 `MarketRepricingSection`을
  렌더한다. forecast artifact/history는 backend compatibility와 shadow research용이다.
- service-contract의 기존 `collector.call_args`는 refresh가 일봉 한 번만 호출한다는 과거
  가정이었다. 새 구현은 활성 trade date에서 별도 5분봉 호출을 할 수 있으므로 interval로
  일봉 호출을 선택해야 일봉 overlap 계약을 안정적으로 검증한다.
- unstaged registry JSONL, untracked saved/run-history, QA 이미지와 `.superpowers/`는
  사용자 또는 local artifact로 보고 건드리지 않는다.
