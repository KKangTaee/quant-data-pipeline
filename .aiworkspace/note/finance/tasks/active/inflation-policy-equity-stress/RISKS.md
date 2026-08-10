# Inflation Policy Equity Stress Risks

- 현재 official EPS vintage 0건을 Shiller trailing EPS로 채우면 PIT·forward 의미가 무너진다.
- 같은 target 수준도 horizon이 없으면 의미가 달라지므로 year-end 기준을 명시한다.
- EPS와 multiple residual을 독립 추출하면 joint downside를 과소평가할 수 있다.
- event study 연관을 금리 인상의 인과효과로 표현하면 안 된다.
- `LIMITED` range를 정밀 probability 또는 목표가로 읽히게 하면 안 된다.
- equity 실패가 기존 물가·정책·금리 또는 5차 침체 상태를 바꾸면 안 된다.
- 사용자 소유 registry, research, run history, QA artifact는 stage하지 않는다.
- label available time을 observation/year-end date로 축약하면 같은 해 미래 label이 학습에
  들어간다. validation fold는 `label_available_at <= evaluation origin`을 유지한다.
- joint path payload만 존재한다고 `READY`로 간주하면 수동 fixture가 publication gate를
  우회할 수 있다. 저장 artifact의 독립 `joint_path_publication_status=READY`와 equity
  publication contract version을 함께 요구한다.
- core model과 joint paths가 같은 component key를 공유하면 다음 core UPSERT가 공동경로를
  제거한다. 공동경로 identity는 `joint_macro_paths`로 유지한다.
- training cutoff가 같아도 일별 snapshot의 지수·EPS·시작금리는 달라진다. live context를
  model artifact에 저장하거나 command가 artifact에서 읽지 않도록 snapshot에만 둔다.
- 일봉에는 publication timestamp가 없으므로 미국 장 마감 전 replay는 당일 close를
  제외한다. 잔차는 path index로 배정하지 않고 순서 독립적인 bounded paired-residual
  quantile sample을 각 path와 교차한다.
- measured EPS revision, 시작금리 또는 공동경로 endpoint 누락을 0으로 해석하면 READY
  분포가 조작된다. 필수 scenario context 완전성 실패는 `NOT_AVAILABLE`이다.

## Closeout

- official EPS vintage와 joint macro path가 아직 없어 actual equity probability는 계속
  `NOT_AVAILABLE`이다. 이는 구현 실패가 아니라 명시적 publication gate다.
- READY 상태의 양·음 AI uplift와 사용자 target interaction은 자동화된 domain/React
  테스트로 검증했으며 실제 Browser에서 임의 fixture를 주입하지 않았다.
- 저장소 전체 `pytest -q`의 Streamlit singleton 순차 격리 부채는 이 task 범위 밖이다.
  이번 변경은 inflation-policy + S&P valuation Python 159건과 React 11건으로 검증했다.
