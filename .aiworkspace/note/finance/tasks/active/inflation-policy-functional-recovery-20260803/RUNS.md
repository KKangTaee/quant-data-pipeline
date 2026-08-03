# Inflation Policy Functional Recovery Runs

## 2026-08-03 Baseline

- `.venv/bin/python -m pytest <inflation-policy 관련 17개 파일> -q`
  - 결과: `190 passed`, 기존 edgar deprecation warning 3건
- `npm test -- --run` in `economic_cycle_workbench`
  - 결과: React `11 passed`
- actual Browser reverse click
  - 결과: `datetime is not JSON serializable`로 component render crash 재현

## 2026-08-03 Recovery Stage 1

- reverse datetime regression RED: raw `datetime` assertion 실패 확인
- component publication regression RED: overall `LIMITED`가 READY inflation까지 숨김 확인
- 수정 후 집중 Python `191 passed`, React `12 passed`, production build 성공
- actual DB reverse command transport: JSON 직렬화 성공, joint path 미존재로 정상
  `NOT_AVAILABLE`
- 기존 서버 Browser 재확인에서 legacy raw session result가 final payload에 붙는 추가
  crash를 재현하고 final transport-edge RED 테스트를 추가했다.
- 최신 코드 전용 `localhost:8502` actual Browser에서 역산 click 후
  `선택한 snapshot과 정확히 일치하는 검증 artifact가 없습니다.`가 정상 표시됐고
  error log 0건을 확인했다.

## 2026-08-03 Recovery Stage 2

- SPF collector/schema/loader RED→GREEN: 12 passed
- 실제 Philadelphia Fed workbook 수집: 1,560 rows, latest survey `2026Q2`, 각 horizon
  10 bins와 약 100% 합계 확인
- direct Q4 target audit에서 inconsistent base-vintage 음수값 재현 후 single-vintage
  target regression 추가
- 실제 Q4 validation: 31 origins, 8 target years, model/SPF weight 0.5/0.5,
  CRPS 0.3613 < prior-year baseline 0.7823, official SPF 0.4217, calibration 0.0484
- 집중 Python suite: 70 passed, 기존 edgar deprecation warning 3건
- React: 13 passed, production Vite build 성공
- actual materialization `2026-08-03T03:15:00Z --persist`: snapshot overall `LIMITED`,
  inflation `READY`, policy `LIMITED`, next release scenarios 5 rows
- actual Browser `localhost:8502`: 5상태/threshold/0.1~0.5 민감도 표시 확인
  - QA: `inflation-policy-core-pce-q4-ready-qa.png`

## 2026-08-03 Recovery Stage 3

- 최초 검토에서 December SEP와 같은 회의의 이미 관측된 연말 결정이 validation target에
  포함된 누수를 발견했다. `release_at < final decision released_at` 회귀 테스트를 먼저
  추가했고 기존 13-origin 수치와 READY 근거를 폐기했다.
- 공식 FOMC historical backfill: 2016~2020 accessible SEP의 외부 table heading·별도 `b`
  release clock·구형 vote/dissent 문구 지원. actual DB는 SEP 40 releases/5,787 rows,
  2016~2026 rate decision 86건이다.
- 누수 제거 policy validation: next-meeting 78 evaluation origins, Brier 0.509346 < best
  baseline 0.516433, ECE 0.068302; year-end 22 evaluation origins(28 completed), Brier
  0.539700 < prior-SEP baseline 0.837982, ECE 0.162442
- 재리뷰 follow-up: historical nonmeeting panel은 discovery에서 제외하고 실제 meeting
  statement의 unknown target syntax는 fail-closed하도록 수정. collector 회귀 포함
  `tests/test_fomc_policy_data.py` 23 passed, actual historical rate statement 41/41 parsed
- joint rate validation: episode 110, endpoint 최소 58 origins. DGS2/DGS10/DFII10/T10YIE
  CRPS가 각각 0.4663/0.3218/0.3684/0.2020으로 각 random-walk baseline보다 낮음
- dynamic resistance reach: 57 origins, Brier 0.131555 < no-change 0.859649,
  ECE 0.159810
- actual materialization `2026-08-03T03:15:00Z --persist`: policy/rates/reverse `READY`,
  `policy_path`와 2,000개 `joint_macro_paths` artifact 저장
- actual reverse command: DGS10 4.79% REACH, probability 0.845, 1,690 supporting paths,
  JSON serialization 성공
- focused Python suite: 163 passed, 기존 edgar deprecation warning 3건
- React: 16 passed, typecheck/build 성공
- actual Browser `localhost:8502`: stored target/form 4.79% 일치, 역산 click 후 84.5%와
  1,690개 경로 표시, component error 없음. 새 snapshot target sync와 같은 snapshot의
  dirty form 보존을 rerender test로 확인
  - QA: `inflation-policy-stage3-leak-free-qa.png`

## 2026-08-03 Recovery Stage 4

- FactSet monthly archive 후보 확인: 2018-01~2026-07 103/103 PDF 경로 발견
- strict two-CY-label 표/OCR 재감사 후 actual DB 저장: 80 release dates, 160 annual EPS rows,
  `2018-01-19~2026-07-31`; archive 후보 103개 중 검증 실패 23개 report는 제외
- 기존 geometry fallback으로 들어간 8 release/16 derived rows를 exact audit 후 제거했다.
  원본 PDF는 보존되며 strict parser가 통과할 때만 재적재된다.
- actual equity validation: completed origin 77, evaluation fold 44, interval fold 32,
  index-change MAE 6.9258 < best baseline 7.6929, 80% interval coverage 0.8125,
  publication `READY`
- actual materialization `2026-08-03T03:15:00Z --persist`: equity `READY`, measured EPS
  revision +1.4242%, index p20/p50/p80 7,654/8,190.6/8,594.9
- actual equity command: user index 6,400, probability `0.02571875`, EPS×multiple target
  decomposition 저장·JSON transport 성공
- focused review fixes: 75 passed; 1~4차 통합 regression `244 passed`(기존 edgar
  deprecation warning 3건); React 17 passed, typecheck/build 성공
- actual Browser `localhost:8502`: S&P panel의 공개시점 EPS 근거, 분포와 `6,400 이하 · 2.6%`
  표시, click crash 없음
  - QA: `inflation-policy-equity-oos-ready-qa.png`

## 2026-08-04 Recovery Stage 5

- FRED/ALFRED `USREC` 2,076 vintage rows 적재. DGS2/DGS10/BAML daily release anchor를
  관측일 EOD로 재정렬하고 DGS2 34,875, DGS10 46,156, BAML 795 rows를 idempotent UPSERT.
- actual recession validation: completed origin 138, OOS fold 86, episode 2,
  Brier 0.146934 < base-rate 0.157162, ECE 0.024324, current completeness 1.0, `READY`.
- actual materialization `2026-08-03T03:15:00Z --persist`: 신규 DB column migration,
  `recession_risk` artifact와 `recession_json` 저장, overall과 6 component 모두 `READY`.
- actual result: 12개월 침체 0.231484, `WATCH/관찰`; top drivers와 OOS metrics read model 통과.
- Python 관련 통합 suite 161 passed, 기존 edgar deprecation warning 3건.
- React 18 passed, TypeScript typecheck와 Vite production build 통과.
- actual Browser `localhost:8502`: 23%·관찰·주요 동인·기존 사이클 미재사용 문구 확인;
  component error 없음. Streamlit route health/host-config 404는 기존 개발서버 소음이다.
  - QA: `inflation-policy-recession-ready-qa.png`
- full rate-clock backfill 뒤 equity fixed-alpha 회귀를 재현: MAE 7.9403 > baseline 7.6929,
  `LIMITED`. nested chronological ridge regression 추가 후 MAE 6.0751, coverage 0.875,
  deployment alpha 100, `READY`; 재-materialization overall `READY`.
