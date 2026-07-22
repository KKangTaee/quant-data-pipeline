# Portfolio Monitoring 로컬 종목 선택 설계

## 이걸 하는 이유?

`종목·전략 결과`에서 항목을 고르는 행위는 서버 데이터를 바꾸지 않는 화면 탐색이다. 현재는
React가 `select_item` event를 Streamlit에 전달하고 Python bridge가 모든 event 뒤에
`runtime.rerun()`을 호출한다. 이 때문에 개별 추적 결과만 바꾸려는 클릭이 포트폴리오
모니터링 전체 재계산과 화면 재생성을 일으킨다.

## 범위

- 종목·전략 결과의 항목 선택은 React 로컬 상태로 처리한다.
- 선택된 항목의 보유내역 요약과 가격 차트가 즉시 함께 바뀐다.
- 그룹 선택, 데이터 최신화, 종목 등록, 추적 종료/취소, 거래 조회·저장은 기존 서버
  event와 전체 재실행 경계를 유지한다.
- DB, registry, 계산식, 거래 command 의미는 바꾸지 않는다.

## 검토한 안

### A. 최대 10개 항목 상세 projection 선적재 — 채택

활성 그룹을 만들 때 이미 계산된 lane으로 항목별 보유내역 projection을 만들고, DB에서
각 직접 종목의 제한된 OHLCV 차트를 함께 조회한다. React는 `selected_item_id`에 맞는
projection만 고른다.

- 장점: 선택 클릭에 서버 event와 rerun이 전혀 없고 반응이 즉시 일어난다.
- 비용: 최초 payload와 DB 조회가 항목 수만큼 늘어난다.
- 완화: 그룹당 최대 10개, 차트당 최대 120행이라는 기존 제품 경계를 그대로 사용한다.

### B. 상세 영역을 별도 Streamlit component/fragment로 분리 — 보류

선택 시 필요한 데이터만 지연 조회할 수 있지만 iframe과 Streamlit 상태 동기화, 화면 높이,
command recovery 경계를 새로 설계해야 한다. 현재 문제에 비해 변경 범위가 크다.

### C. 전체 rerun을 유지하고 cache만 강화 — 제외

계산 시간은 줄일 수 있지만 전체 화면이 다시 그려지는 사용성 문제는 남는다.

## 데이터 계약

workspace에 다음 additive field를 추가한다.

```text
item_details: {
  <monitoring_item_id>: {
    position: SelectedPositionProjection,
    market_chart: SelectedItemMarketChart | null
  }
}
```

- 모든 항목은 `position`을 가진다. 거래 비대상 전략/ETF/투자금 방식은 기존과 동일한
  `eligible: false`와 이유를 반환한다.
- `market_chart_loader`가 있는 화면 workspace에서는 각 항목의 `market_chart`를 만든다.
  전략은 기존 `UNSUPPORTED` projection을 통해 그룹 가치곡선을 쓰도록 구분한다.
- 기존 `selected_position`, `selected_item_market_chart`는 Python/구 build 호환을 위해
  유지한다.
- React는 `item_details[selectedItemId]`를 우선 사용하고, field가 없는 이전 payload에서는
  기존 selected field를 fallback으로 사용한다.

## 변경 후 흐름

```text
workspace 최초 로드
  -> 활성 그룹의 최대 10개 항목 상세 projection 생성
  -> React가 workspace를 렌더링
  -> 사용자가 항목 행 클릭
  -> setSelectedItemId(itemId)
  -> 개별 추적 결과의 position/chart만 해당 projection으로 교체
```

종목별 거래 action을 누르면 event 자체에 `monitoring_item_id`가 포함되므로 Python이 현재
선택 항목을 다시 식별하고 command를 실행한다. command 완료 후 새 workspace에서도 같은
항목을 선택하도록 기존 session recovery를 유지한다.

## 오류와 호환성

- 한 종목 차트 조회 실패는 그 종목의 `ERROR` projection으로 격리하고 다른 항목 선택을
  막지 않는다.
- 항목 id가 map에 없거나 구 payload인 경우 기존 selected projection이 같은 id일 때만
  사용한다. 일치하지 않으면 기존 로딩 상태를 표시한다.
- `select_item` Python dispatcher는 구 component build 호환을 위해 당장 제거하지 않는다.
  새 React build만 이 event를 보내지 않는다.

## 검증

- Python: 모든 활성/종료 항목의 상세 map과 항목별 차트 격리, loader 미설정 경계를 검사한다.
- React: 선택 id에 따른 detail 선택과 legacy fallback을 검사한다.
- source contract: `chooseItem`이 `select_item` event를 emit하지 않는지 검사한다.
- 회귀: Portfolio Monitoring Python/React 전체 테스트, typecheck, production build를 실행한다.
- Browser QA: 서로 다른 두 종목을 선택했을 때 외부 페이지 scroll 위치와 그룹 영역은
  유지되고 개별 추적 제목·차트만 즉시 바뀌는지 확인한다.

## 잠정 개발 차수

1. 상세 projection 계약과 회귀 경계를 고정한다.
2. Python projection과 React 로컬 선택을 구현한다.
3. 브라우저 QA, 문서 동기화, 최종 통합 검증을 수행한다.

