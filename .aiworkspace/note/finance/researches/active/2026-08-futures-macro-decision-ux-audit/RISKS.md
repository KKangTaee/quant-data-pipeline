# Futures Macro Decision UX Audit — Risks

State: complete

## 구현 전 통제할 위험

### Shared header 회귀

공통 `market_research_header/style.css`를 전역 수정하면 다른 Market Research 화면의 hero가 바뀔 수 있다.
Futures Macro 전용 class 또는 variant로 범위를 제한해야 한다.

### 장중 세션과 finalization 혼동

장중 5분봉 수집 여부와 완료 일봉 확정 가능 여부는 서로 다른 판단이다. 하나의 daily probe 상태로 둘을
동시에 제어하면 저녁 재개장이나 미래 trade-date 세션을 놓친다.

### 휴장일 오인

trade-date resolver가 거래소 휴장을 완전히 판별하지 못할 수 있다. active 후보 세션에서 새 5분봉이
없으면 최신 완료 세션을 유지하고, 불완전 데이터를 현재 관측으로 승격하지 않는 방어가 필요하다.

### `NO_EDGE` 의미 왜곡

`확인 안 됨`은 검증 미실행과 검증 실패를 혼동한다. `INSUFFICIENT_DATA`, `NO_EDGE`, `VERIFIED`의 copy와
UI 상태를 분리해야 한다. 임계값을 낮춰 겉으로 VERIFIED를 늘리는 방식은 사용하지 않는다.

### 시간축 narrative 과장

1D/5D/20D 문장은 원시 family 상태로부터 결정적으로 생성되어야 한다. LLM식 자유 문장이나 근거 없는
인과 표현은 피하고, 강화/완화/지속/반전/혼재/무변화의 제한된 어휘로 만든다.

### 정보 삭제에 따른 근거 손실

Next Check를 제거하더라도 계산 범위와 임계값을 완전히 숨기지는 않는다. 방법론 disclosure에서
재현 가능한 근거를 유지하되 기본 판단 흐름에서는 접는다.
