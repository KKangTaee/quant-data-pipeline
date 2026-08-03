# Economic Cycle Usability Follow-up V2 Design

Status: User-approved
Last Updated: 2026-08-04

## Diagnosis

2026-08-04 수동 실행은 17개 요청, 17개 처리, 실패 0개로 성공했으며 총
96.836초가 걸렸다. 따라서 버튼은 고장난 것이 아니라 provider 수집, 닫힌 월
rollover, PIT/revised panel 재계산과 월중 snapshot 저장을 동기 실행해 느린 상태다.
일반적인 비월말 실행도 약 42~45초가 걸린다.

현재 공식 월말 snapshot은 `contraction`, transition anchor는 `recovery`, target은
`expansion`, 조건은 0/3, `non_adjacent_observation = true`다. 이 조합은 기존 순차
transition state machine상 유효하다. 그러나 `expansion`은 회복 앵커의 다음 인접
국면이지 확률적으로 가장 유력한 예측이 아니다. 기존 UI가 이 경계를 충분히
설명하지 못했다.

## Considered Approaches

### A. Current-observed-first — adopted

현재 관측 국면과 지속기간을 주 정보로 표시하고, 앵커·구조적 target은 보조
reference로 내린다. 비인접 관측이면 불일치를 명시하고 지도 화살표는 현재 관측
국면의 다음 인접 국면을 가리킨다.

### B. Anchor-first copy expansion

기존 `회복 → 확장` 레이아웃을 유지하고 설명만 늘린다. 변경은 작지만 현재 위축을
보는 사용자가 확장을 유력 예측으로 오해하는 핵심 문제를 남겨 채택하지 않는다.

### C. Non-adjacent anchor reset

비인접 관측이 나오면 즉시 앵커를 현재 국면으로 재설정한다. 화면은 단순해지지만
확정 조건을 건너뛰어 기존 persistence 계약을 훼손하므로 채택하지 않는다.

## Freshness Contract

Freshness bar는 아래 시점을 분리한다.

- `last_checked_at`: provider 확인을 실행한 시각
- `persisted_as_of_date`: 월중 계산 cutoff
- `latest_source_observation_date`: 실제 계산에 포함된 원천 중 최신 관측일
- 공식 국면 기준일은 hero의 month-end `as_of_date`로 유지한다.

버튼은 `최신 발표 확인·재계산`으로 명명하고 `보통 1분 내외`를 사전에 알린다.
클릭 후에는 `원천 확인과 재계산 중 · 보통 1분 내외`를 즉시 표시한다. 별도 run/job
진단 패널은 만들지 않는다.

평일 cutoff 기반 refresh eligibility는 이번 범위에서 유지한다. release calendar를
모든 series에 연결하지 않은 상태에서 신규 발표 여부를 미리 확정하면 false negative가
생길 수 있기 때문이다. 대신 `오늘 확인했다`와 `원천 관측일이 오늘이다`를 같은
의미로 표시하지 않는다.

## Actual Cycle Map Contract

service는 12개월 `cycle_map.points`를 계속 제공해 리본에 사용한다. Quadrant chart만
다음 네 checkpoint를 선택한다.

```text
6개월 전 -> 3개월 전 -> 1개월 전 -> 현재
```

데이터가 짧으면 존재하는 지점만 중복 없이 사용한다. 각 점은 날짜, 국면, level,
momentum tooltip을 유지한다.

지도 화살표는 확률 예측이 아니라 structural direction reference다.

- anchor와 observed가 인접하면 monitor target을 사용한다.
- `non_adjacent_observation`이면 현재 observed phase의 다음 인접 국면을 사용한다.
- 현재 `위축` 사례에서는 `회복` 방향을 가리킨다.

## Transition Card Contract

카드 제목은 `현재 관측과 전환 기준`으로 바꾼다.

첫 블록:

- 현재 관측 국면
- 현재 국면 지속 개월
- 앵커와 비인접이면 `모델 기준과 불일치 · 지속 여부 재확인` 표시

두 번째 reference 블록:

- 전환 기준 앵커와 기준일
- anchor basis: `INITIALIZED`, `CONFIRMED`, `LEGACY_OBSERVED`, `UNKNOWN`
- 앵커 기준 구조적 다음 국면
- candidate observation 시작일

condition grid는 일반적인 `다음 국면 조건`이 아니라 정확한
`anchor -> target 확인 조건`이라고 표시한다. target은 높은 확률의 forecast가
아니라는 문장을 항상 붙인다.

새 materialization은 anchor가 처음 만들어진 시점과 확인 근거를 저장한다.

```text
anchor_started_at
anchor_source = INITIALIZED | CONFIRMED
anchor_confirmed_at
```

legacy snapshot은 service가 history에서 confirmed transition을 우선 찾는다. 찾지
못하면 현재 조회 구간에서 anchor가 처음 관측된 날짜를 `LEGACY_OBSERVED`로 표시하며
확정일로 가장하지 않는다.

## Regime Ribbon Contract

범례는 회복(파랑), 확장(초록), 둔화(주황), 위축(빨강), NBER 침체 음영을 모두
표시한다. 각 월은 hover와 keyboard focus에서 아래 정보를 보여준다.

- YYYY년 MM월
- 관측 국면
- NBER 침체/비침체
- 판단 신뢰도와 수정 민감도

native `title`만 의존하지 않고 화면 안 custom tooltip을 사용한다.

## Asset Surface Freeze

`자산별 확인 포인트`의 payload, markup, copy, card order와 CSS는 수정하지 않는다.
React 회귀 테스트에서 다섯 자산 블록의 존재와 순서를 계속 확인한다.

## Validation

- observed-state domain metadata red/green tests
- service legacy/current anchor metadata와 freshness metadata tests
- React checkpoint, transition semantics, phase legend/tooltip tests
- focused Python suite, React test, TypeScript/Vite production build
- `git diff --check`
- live Streamlit Browser QA와 screenshot 1장
