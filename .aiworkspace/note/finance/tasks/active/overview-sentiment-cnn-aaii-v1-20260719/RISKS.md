# Risks

- CNN은 여러 시장 행동 지표의 종합값이므로 구성요소를 별도 독립 축처럼 다시 합산하면 이중 반영된다.
- AAII 주간 설문과 CNN 일간 지표의 변화 속도를 직접 비교하거나 같은 선으로 연결하지 않는다.
- 최근 범위 percentile은 저장된 표본 내 위치이며 장기 역사 percentile이나 미래 예측으로 표현하지 않는다.
- `+10pp / -10pp` AAII spread 경계는 제품의 deterministic 해석 규칙이며 투자 수익 예측 임계값이 아니다.
- 1차에서 제공하는 확인 조건은 관찰 checklist이지 목표가격, 매매 신호, 확률 전망이 아니다.
- 2차에서 발표 당시 값과 수정 이력, 장기 coverage가 충분히 축적되기 전에는 최근 percentile을 역사적 극단값처럼 해석하지 않는다.
- 1주·1개월 전망은 별도 point-in-time feature/target 정의와 chronological out-of-sample 검증 없이는 추가하지 않는다.
- AAII 표본과 CNN 산출 방법의 source-side 변경 가능성은 freshness / raw evidence와 후속 품질 점검에서 계속 확인한다.
- 시각 companion의 1W·1M 확률은 production 근거로 재사용하지 않는다. estimator와 validation evidence가 없으면 UI는 반드시 `UNAVAILABLE`을 표시하고 확률 field를 렌더링하지 않는다.
- frontend fallback은 rolling reload 시 component crash를 막는 unavailable 표시일 뿐이며 전망 evidence를 대체하지 않는다. 정상 전망 공개 여부는 Python의 validation gate가 소유한다.
- 3차 변화량은 저장된 관측 간 차이이지 미래 성과나 다음 기간 방향이 아니다. 화면 문구에서 `전망`, `확률`, `예상`으로 오해시키지 않는다.
- CNN 5/20개와 AAII 1/4개는 동일 날짜 구간을 강제한 값이 아니라 각 source의 관측 주기에 맞춘 비교다. 실제 시작·종료일을 함께 표시한다.
- 전체 sentiment 선택 테스트 baseline에는 이번 작업과 무관한 AAII parser expectation 1건, Practical Validation overlay expectation 2건이 이미 실패한다. 3차의 완료 판단은 focused 계약과 변경 파일 검증을 사용하고 기존 실패를 숨기지 않는다.
- 4차에서 전망을 연결하더라도 3차 observed change card를 확률로 재해석하지 않는다. target과 독립 episode, chronological validation evidence가 없는 전망은 기존 `outlook` gate에서 계속 차단한다.
- 동일 관측일에 여러 source/version이 들어오면 수집 시각 없는 row보다 명시된 최신 `collected_at`을 우선한다. 최신 version이 결측인 경우 이전 유효 version으로 조용히 대체하지 않고 해당 기간을 unavailable로 닫는다.
- 서비스가 숫자를 제공해도 source별 시작·종료 날짜가 누락·invalid이거나 역전되면 payload에서 unavailable로 닫는다. 날짜 없는 변화량을 실제 기간 변화처럼 공개하지 않는다.
