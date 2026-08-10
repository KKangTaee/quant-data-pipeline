# Inflation Policy Functional Recovery Status

State: complete
Roadmap: 5/5 recovery stages complete
Last Updated: 2026-08-04

## Current

- 사용자 재현 6개 증상과 actual DB 상태를 기준으로 기존 완료 기록을 재감사했다.
- 기존 집중 baseline은 Python 190건, React 11건 통과했지만 actual reverse click과
  production materialization contract를 포함하지 않았음을 확인했다.
- 승인된 복구 설계와 5차 roadmap을 기록했다.
- reverse command result를 payload 저장 전 JSON-safe하게 정규화했다.
- React가 snapshot 전체 상태가 아니라 inflation/policy component별 상태로 확률을
  표시하도록 복구했다.
- actual DB reverse command 결과가 `datetime`을 문자열로 변환하고 JSON 직렬화되는지
  확인했다. joint path 부재로 결과 자체는 정확히 `NOT_AVAILABLE`이다.
- Philadelphia Fed SPF Core PCE `PRCPCE` 공식 확률분포 1,560개 bin을
  `spf_core_pce_probability`에 PIT release clock과 함께 적재했다.
- chain-price index rebasing 때문에 서로 다른 최초공개 level을 섞으면 2018/2023 Q4가
  음수로 왜곡되는 문제를 찾고, December 최초 공개시각의 단일 일관 vintage로 실제
  Q4/Q4 target을 계산하도록 수정했다.
- 2018~2025 31개 조사 origin·8개 독립 target year에서 SPF+월별 모델 linear pool을
  직접 검증했다. CRPS 0.3613, 단순 전년 Q4 baseline 0.7823, SPF 단독 0.4217,
  최대 interval calibration error 0.0484로 `READY`다.
- actual 2026-08-03 snapshot의 inflation component를 `READY`로 저장했고 5상태,
  3.4/3.5/3.6% threshold, 다음 발표 0.1~0.5% 민감도를 Browser에서 확인했다.
- 공식 FOMC current calendar와 2016~2020 historical material을 함께 수집해 실제
  rate decision 86건과 SEP 40개 release·5,787개 distribution row를 저장했다.
  historical 외부 heading, 별도 공식 release clock과 당시 vote/dissent 문구를 파싱하며
  balance-sheet/strategy statement는 제외한다.
- 최초 연말 검증에 12월 SEP와 같은 회의의 이미 관측된 연말 결정이 섞인 누수를
  발견해 `SEP released_at < final decision released_at`으로 차단했다. 기준을 낮추지 않고
  과거 공식 자료를 backfill한 뒤 다음 회의 78개, 연말 22개 평가 origin에서 재검증했다.
  다음 회의 Brier 0.5093은 best baseline 0.5164보다 낮고, 연말 Brier 0.5397은 prior-SEP
  baseline 0.8380보다 낮아 `policy_path`가 누수 없이 `READY`다.
- 2016~2025 completed monthly episode 110개로 DGS2/DGS10/DFII10/T10YIE endpoint와
  동적 저항 도달 event를 시간순 검증했다. 각 endpoint CRPS가 random-walk
  baseline보다 낮고 저항 event 57개 origin Brier 0.1316이 baseline 0.8596보다 낮아
  `joint_macro_paths` 2,000개를 `READY`로 저장했다.
- actual 2026-08-03 snapshot에서 inflation/policy/rates/reverse가 모두 `READY`다.
  다음 DGS10 overhead는 고정 4.7%가 아닌 4.79%이며, 기본 도달 역산은 확률 84.5%,
  지지 경로 1,690개다.
- Browser에서 저장된 4.79% target과 form 초기값을 일치시킨 뒤 `필요 경로 역산`을
  눌러 같은 조건부분포가 표시되고 component crash가 없음을 확인했다. 새 snapshot은
  form을 새 target으로 동기화하고 같은 snapshot의 command 결과는 사용자가 수정 중인
  입력을 덮어쓰지 않도록 보완했다.
- FactSet Earnings Insight의 날짜가 붙은 월별 보고서를 backfill해 검증 가능한 공개시점
  80개와 current/next-calendar-year 연간 bottom-up EPS 160행을 저장했다. archive 후보
  103개 중 표·두 CY 라벨을 검증하지 못한 23개는 숫자를 추정하지 않고 제외했다.
- 77개 completed equity origin으로 공개시각 rolling validation을 수행했다. 지수 변화
  MAE 6.9258%가 best baseline 7.6929%보다 낮고, 과거 OOS 잔차만 사용한 80% interval
  coverage가 0.8125(32 folds)로 gate를 통과해 equity가 `READY`다.
- actual snapshot에서 measured next-year EPS revision +1.4242%, index p20/p50/p80
  7,654/8,190.6/8,594.9를 저장했다. Browser에서 사용자 6,400 조건을 실행해 동일
  snapshot/artifact 기준 `6,400 이하 2.6%`(exact 2.5719%)와 EPS×multiple 분해가 표시되고 crash가
  없음을 확인했다.
- 일별 미개정 Treasury series의 PIT clock이 ALFRED 데이터셋 등록일로 잘못 잡혀
  1988~2005 금리곡선을 누락한 원인을 수정했다. 관측일 EOD release anchor로 DGS2/DGS10을
  재적재하되 revision interval identity는 보존했다.
- 독립 침체 모델은 1989~2023 completed origin 138개, chronological OOS fold 86개와
  독립 침체 episode 2개를 평가했다. Brier 0.146934 < base-rate 0.157162,
  calibration error 0.024324, current feature completeness 1.0으로 `READY`다.
- 2026-08-03 snapshot의 향후 12개월 침체 확률은 23.1484%, 5단계 상태는 `WATCH/관찰`이다.
  `USREC`은 24개월 지연 outcome label로만 쓰고 기존 경제 사이클 확률·artifact·snapshot은
  import/query/fallback하지 않는다.
- 모든 일별 금리 PIT clock 수정 직후 기존 고정 ridge는 MAE 7.9403으로 baseline을 못 이겨
  `LIMITED`가 됐다. outer 평가를 보지 않는 nested chronological inner-fold ridge 선택으로
  수정한 뒤 77 origins/44 folds, MAE 6.0751 < baseline 7.6929, OOS 80% coverage 0.875로
  다시 `READY`임을 확인했다. 배포 alpha는 inner-fold가 선택한 100이다.
- 실제 DB read model에서 inflation/policy/rates/reverse/equity/recession과 overall이 모두
  `READY`다. Browser에서 침체 23%·관찰·주요 동인과 기존 사이클 미재사용 문구를 확인했다.

## Next

- 기능 복구 5단계는 종료한다. 이후는 새 범위가 아니라 정기 raw refresh와 동일
  materialization 명령으로 최신 snapshot을 갱신한다.
