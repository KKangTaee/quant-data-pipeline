# Economic Cycle Provisional Hybrid V2 Notes

Last Updated: 2026-07-16

- V1은 LIMITED horizon의 확률·dominant phase를 snapshot에서 제거했다.
- 실제 artifact에는 horizon별 모델 parameter와 validation reason이 남아 있다.
- V2는 threshold를 낮추지 않고 계산 결과와 검증 상태를 분리한다.
- 2×2 좌표는 네 국면 확률의 성장 레벨·모멘텀 projection을 사용한다.
- Model public prediction API의 LIMITED 거부는 유지한다. Pipeline이 validation status를 바꾸지 않은 scoring copy를 명시적으로 사용한다.
- Early replay artifact는 missing phase support로 parameter map이 불완전할 수 있다. 해당 horizon은 전체 replay를 중단하지 않고 `UNAVAILABLE`로 남긴다.
- 후속 UX 조정으로 Cycle Map은 최근 12개월, Regime Ribbon은 최근 60개월만 표시한다. DB의 121개월 replay snapshot은 보존한다.
- 60개월 전환 직후 CSS grid가 121개 history 열을 고정해 ribbon이 절반만 채워졌다. 실제 `history.length`를 CSS custom property로 전달해 partial/60개월 payload 모두 전체 너비를 사용한다.
- 빈 history에는 명시적인 과거 placeholder를 두고 +1M/+2M은 고정 slot으로 렌더링한다. 따라서 h1만 누락돼도 h2가 앞당겨지지 않는다.
- Cycle Map의 과거/forecast 확률점은 hover 또는 keyboard focus 때만 날짜·우세 국면·확률·추정 상태를 표시한다. 결측점에는 tooltip을 합성하지 않는다.
- 최근 12개월 경로와 현재·+1M·+2M 전망 경로는 결측점을 제거해 연결하지 않는다. 결측점에서 선분을 끊어 존재하지 않는 이동을 합성하지 않는다.
- Long-running Streamlit process가 old service payload를 보낼 수 있어 React는 `estimate_status`가 없으면 publication status와 probabilities로 동일 상태를 복원한다.
