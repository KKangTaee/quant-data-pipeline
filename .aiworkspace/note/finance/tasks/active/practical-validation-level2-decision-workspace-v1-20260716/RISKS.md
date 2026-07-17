# Risks

- finding_kind가 raw status와 별도 truth source가 되면 분류 drift가 생길 수 있다. closure resolution class와 audit applicability를 입력으로만 사용하고 UI에서 재계산하지 않는다.
- accepted limit를 지나치게 넓게 허용하면 중요한 evidence gap을 Final Review 판단으로 우회할 수 있다. criticality와 applicability가 먼저 Gate를 결정해야 한다.
- current two-component React surface를 즉시 삭제하면 legacy source contract와 fallback 회귀가 커질 수 있다. active render를 먼저 교체하고 물리 삭제는 usage audit 후 결정한다.
- source / profile / replay intent를 React에 노출해도 Python session과 current validation id를 재검증하지 않으면 stale action이 실행될 수 있다.
- single component 100%와 underlying holdings concentration을 구분하지 않으면 포트폴리오 성격을 잘못 설명할 수 있다.
- 긴 raw evidence를 one-shell에 다시 모두 넣으면 Final Review 개편 전과 같은 card / guide 과잉으로 돌아갈 수 있다.
- 실제 PASS audit row를 모두 first-read 카드로 펼치면 다시 정보 과잉이 될 수 있다. first-read verified card는 최대 8개로 제한하고 전체 row는 disclosure에서 확인한다.
- structured measurement가 없는 prose를 `measured_caution`으로 해석하면 숫자를 발명하게 된다. observation과 threshold / comparator가 모두 있는 경우만 해당 finding_kind를 만든다.
- React build와 Python payload schema를 함께 변경한 뒤 장기 실행 Streamlit process가 stale module / bundle을 들 수 있으므로 Browser QA 전 재기동이 필요하다.
- protected registry와 run history는 사용자 실사용 결과다. 구현 / QA / docs commit에서 stage하거나 rewrite하지 않는다.
- `npm install`은 transitive dependency에서 moderate 1건, high 1건을 보고했다. `npm audit fix --force`는 Vite / Streamlit component compatibility를 깨뜨릴 수 있어 이번 scope에서 실행하지 않았으며 별도 dependency upgrade 검토가 필요하다.
- legacy Fix Queue / Data Action Board는 active path에서 제거됐지만 물리 파일은 남아 있다. usage audit 없이 삭제하지 않는다.
- `validated_caution`을 raw `REVIEW`만 보고 만들면 미구현 validator를 다시
  통과시킬 수 있다. producer가 explicit `evidence_state`를 제공하고 closure는
  누락 시 보수적으로 engineering-required로 분류한다.
- fragment rerun은 replay 실행 중 상단 context를 보존하지만 Final Review route
  이동은 app rerun이어야 한다. 모든 intent를 fragment scope로 강제하지 않는다.
- Final Review의 private explanation helper를 직접 import하면 stage 간 결합이
  생긴다. Level2 pure explanation service가 필요한 mapping을 독립적으로 소유한다.
- iShares workbook과 Vanguard JSON은 provider-owned payload 계약이다. column
  label이나 response envelope가 바뀌면 verification이 empty/malformed payload를
  거부하고 Level2가 다시 engineering blocker로 남겨야 한다.
- 공식 holdings는 current snapshot이다. 8개 ETF의 최신 coverage가 생겼어도
  historical point-in-time membership / delisting truth를 증명하지 않는다.
- VNQ provider snapshot의 weight 합은 99.45%다. 이를 억지로 100% 정규화하지
  않고 provider 원문 coverage로 보존하며, 후속 분석은 residual을 고려해야 한다.
- 지정 후보를 Browser QA에서 저장하지 않았으므로 Final Review registry에는
  이번 session validation row가 append되지 않았다. 사용자가 Step 4 저장·이동을
  실행해야 해당 validation_result_id가 durable handoff source가 된다.
- provider source-map discovery 시도 여부는 bounded run history를 읽어
  반복 CTA를 방지한다. 장기적으로 이 lifecycle을 durable source-contract
  상태에 저장할지 검토할 수 있지만, protected run history/schema 재설계는
  이번 범위 밖이다.
- 현재 lookup은 전역 run history 최근 500건 범위다. 다른 pipeline 실행이
  누적되어 failed/exception discovery 기록이 범위 밖으로 밀리면 같은 CTA가
  장기적으로 다시 나타날 수 있다. durable source-attempt persistence는
  schema/source-contract 확장 승인이 필요한 후속 위험이다.
- partial-month Monitoring 판정은 월 단위 cadence 계약이다. 월간 전략이 아닌
  다른 cadence가 같은 필드를 쓰게 되면 strategy cadence를 explicit input으로
  확장해야 하며, 현재는 설명되지 않은 장기 gap을 보수적으로 차단한다.
- 공통 가격일의 월말 허용 범위는 주말/휴장을 포함한 7일이다. 비월간 cadence나
  더 긴 시장 휴장이 필요한 source는 이 숫자를 재사용하지 말고 source cadence
  contract를 별도로 제공해야 한다.
- correction desktop / 760px Browser QA가 남아 있다. 8506 stale no-watch process를
  current commit으로 재시작한 뒤 in-app Browser local URL security policy가
  reload와 snapshot을 차단했다. automated 188-test suite와 두 production build는
  통과했지만 실제 replay pending → 결과 shell 유지, accepted-limit 선택,
  return-to-Level2 route, 760px overflow는 같은 current build에서 다시 확인해야 한다.
- `fileWatcherType none` QA server는 React/Python 계약을 함께 바꾼 뒤 반드시
  재기동해야 한다. 그렇지 않으면 새 bundle이 stale read model을 받아 component
  error처럼 보일 수 있으며, 이는 배포 bundle 자체의 schema fallback을 대신하지 않는다.
