# Futures Macro Repricing Radar V1 Design

State: approved
Last Updated: 2026-08-17

## 승인 기록

- 사용자는 `시장 재가격화 레이더로 개편` 권장안 1을 승인했다.
- `현재 흐름을 향후 5거래일로 연장할 수 있는가?`는 필요하지 않으므로 제거하도록 명시했다.

## 제품 약속

선물 매크로는 미래 가격을 맞히는 화면이 아니다. 주가지수·국채·FX·원자재 선물의
1D·5D·20D 움직임을 연결해 다음을 끝내는 조사 화면이다.

1. 지금 새로 나타난 변화
2. 현재 재가격화의 중심축
3. 그 해석을 지지하거나 반박하는 다른 선물군
4. 현재 해석이 이어지거나 무효화되는 조건과 민감 자산

## 판단 구조

- core 4개: 위험선호, 금리 부담, 달러 압력, 물가 압력
- confirmation 2개: 성장 기대, 방어 수요
- 5D 절대값이 가장 큰 material core를 해석의 중심축으로 선택한다.
- 나머지 core는 위험선호 정규화 방향으로 supporting/counter evidence를 나눈다.
- confirmation은 겹치는 구성 종목 때문에 독립 확인 개수로 세지 않고 맥락 근거로만 쓴다.
- 1D가 중심 5D 방향과 반대이고 둘 다 material하면 반대 근거에 포함한다.
- material 5D core가 없지만 1D core가 뚜렷하면 `NEW_SHOCK`, 1D도 중립이면 `LOW_SIGNAL`, finite core가 없으면 `UNAVAILABLE`다.

## 화면 구조

```text
Hero / data provenance
  -> 시장 재가격화 흐름 (1D / 5D / 20D)
  -> 시장 재가격화 해석
       유력한 해석
       반대 근거
       조건부 시나리오
  -> 선물군별 방향 정렬
  -> 최근 체제 이력
  -> 관측 방법론과 품질
  -> 원본 데이터 / 계산 추적
```

조건부 시나리오는 확률이나 5D 가격 목표가 아니다. `지속 조건`, `무효화 조건`,
`민감 영역`만 제시한다. 과거 forecast validation과 immutable history는 삭제하지 않고
backend shadow evidence로 보존한다.

## 사용자 문장 원칙

- `금 상승 = 인플레이션`처럼 단일 자산의 인과를 확정하지 않는다.
- family 산식의 실제 기반 종목을 함께 밝힌다.
- 유력 해석과 반대 근거를 같은 화면에 둔다.
- `확인하세요` 같은 일반 안내 대신 어떤 방향이 유지·반전되면 해석이 달라지는지 쓴다.
- `예측`, `확정`, `매수`, `매도`를 결과 문구로 사용하지 않는다.

## 데이터와 안전 경계

- 장중 fresh 5m은 현재 관측에만 사용한다.
- 마지막 완료 일봉 fallback과 기준 시각을 유지한다.
- future validation은 completed daily만 사용하지만 기본 화면에서는 노출하지 않는다.
- continuous futures roll, 무료 provider, family overlap 한계를 방법론에 유지한다.
- 투자 추천, 주문, monitoring signal로 승격하지 않는다.

## 제외 범위

- forecast model 또는 publication threshold 수정
- DB schema와 forecast history 삭제
- term structure, SOFR, TIPS, options, CFTC positioning 추가
- LLM 자유 생성 문장
- 자동 매매와 포트폴리오 추천
