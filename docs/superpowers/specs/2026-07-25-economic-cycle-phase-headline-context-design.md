# Economic Cycle Phase Headline Context Design

Status: Approved Direction
Date: 2026-07-25

## 이걸 하는 이유?

현재 hero의 `회복 우세`와 `현재는 회복 국면 가능성이 가장 높습니다.`만으로는
생산·소비와 고용·소득 수준이 낮은데도 왜 회복인지 바로 이해하기 어렵다. 사용자가
별도의 모델 설명을 읽지 않아도 국면의 `수준 × 최근 3개월 방향` 의미를 첫 화면에서
이해하게 한다.

## User-Facing Design

hero 제목은 현재처럼 짧은 국면 판정을 유지한다.

```text
회복 우세
```

hero 설명은 dominant phase에 맞는 수준·방향 설명으로 바꾼다.

| Phase | Hero description |
|---|---|
| recovery | 생산·소비와 고용·소득 수준은 낮지만 최근 3개월 흐름은 개선 중입니다. |
| expansion | 생산·소비와 고용·소득 수준이 높고 최근 3개월 흐름도 개선 중입니다. |
| slowdown | 생산·소비와 고용·소득 수준은 높지만 최근 3개월 흐름은 약화 중입니다. |
| recession | 생산·소비와 고용·소득 수준이 낮고 최근 3개월 흐름도 약화 중입니다. |

현재 결과가 없거나 국면을 판정할 수 없으면 기존 제한 문구를 유지한다.

## Ownership And Data Flow

- `app/services/overview/economic_cycle.py`가 phase별 사용자 설명을 소유한다.
- React는 `payload.headline.summary`를 그대로 표시한다.
- 확률 카드, 월중 비교, cycle map, ribbon의 짧은 `회복/확장/둔화/침체` 표기는
  변경하지 않는다.
- 저장 snapshot schema, 모델 feature, 확률, DB, provider 수집은 변경하지 않는다.

## Testing

- service test에서 네 phase별 headline summary mapping을 검증한다.
- 기존 Economic Cycle service/UI regression과 React production build를 실행한다.
- actual browser에서 hero가 `회복 우세`와 회복 설명을 함께 표시하는지 확인한다.
- 420px에서 줄바꿈과 가로 overflow를 확인하고 QA screenshot 한 장을 남긴다.

## Non-Goals

- 국면 산식이나 probability 변경
- Evidence·자산 카드 문구 재설계
- 확률 카드와 차트의 모든 phase label 확장
- 운영 진단 패널 또는 데이터 최신화 기능 변경
