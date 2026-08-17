# Overview Sentiment Watch Guide Removal Design

## Status

- Date: 2026-08-11
- Decision: approved by the user
- Roadmap position: 3/4차 후속 UI 정리

## 이걸 하는 이유?

`Market Research > 심리` 하단의 `WATCH / 다음 확인 조건`은 실제 monitoring,
alert, condition persistence를 수행하지 않는다. 현재 관측을 어떻게 다시 확인할지
설명하는 정적 해석 가이드이며, 사용자는 이 화면에서 해당 가이드를 노출할 필요가
없다고 결정했다.

기능처럼 읽히는 장식을 유지하면 사용자가 자동 감시나 알림이 존재한다고 오해할 수
있다. 기간별 실제 변화와 상세 근거만 남겨 화면을 더 짧고 정확하게 만든다.

## 선택한 접근

UI-only removal을 적용한다.

- `SentimentWorkbench`에서 `WatchConditionsSection` import와 render를 제거한다.
- 더 이상 소비되지 않는 `WatchConditionsSection.tsx`를 삭제한다.
- `.sentiment-workbench__watch-grid` 전용 CSS와 공용 surface selector 연결을 제거한다.
- 화면 순서는 `기간별 심리 변화 -> 상세 근거와 원본 데이터`로 단순화한다.

Python service가 만드는 `watch_conditions`와 React payload type은 이번 변경에서
삭제하지 않는다. 사용자의 요구는 현재 화면 노출 제거이며, payload 제거는 service
contract와 잠재 consumer를 함께 바꾸는 별도 범위다.

## 검토한 대안

1. CSS로 숨기기: 화면에서는 사라지지만 component와 테스트가 죽은 상태로 남으므로
   채택하지 않는다.
2. service/payload까지 end-to-end 삭제: 더 깔끔하지만 이번 사용자 요구보다 범위가
   크고 backward compatibility 검토가 필요해 채택하지 않는다.
3. 상세 disclosure 안으로 이동: 사용자는 가이드를 여기서 보여주지 않아도 된다고
   했으므로 불필요한 정보 이동으로 판단한다.

## 테스트와 QA

- source-contract는 root에서 Watch import/render가 없고 component 파일과 전용 CSS가
  제거됐음을 검증한다.
- backend `watch_conditions` 생성과 payload 테스트는 호환 계약으로 유지한다.
- Vite production bundle을 재생성한다.
- actual Streamlit Browser QA에서 기간별 변화 바로 다음에 상세 disclosure가 나오고,
  `WATCH`, `다음 확인 조건`, 세 guide card가 보이지 않는지 확인한다.
- desktop과 420px에서 overflow와 console warning을 확인한다.

## 비범위

- 신규 monitoring, alert, watchlist 기능
- `watch_conditions` service 계산과 payload schema 삭제
- 기간 변화 계산, CNN/AAII 판정, 전망 publication gate 변경
- 4차 estimator와 validation 개발

## 완료 조건

- 심리 화면에서 Watch guide section이 완전히 사라진다.
- 기간 변화와 상세 근거는 그대로 동작한다.
- 삭제된 UI를 요구하던 회귀 테스트가 새 부재 계약으로 전환된다.
- production build와 Browser QA가 통과한다.
