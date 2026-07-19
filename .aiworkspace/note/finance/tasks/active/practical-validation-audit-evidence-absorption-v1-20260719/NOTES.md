# Notes

## Decisions

- raw source/replay/validation data는 삭제하지 않고 current Level 2 raw rendering만 제거한다.
- 후보 의미는 Step 1, replay provenance는 Step 2, validation record identity는 Step 4가 소유한다.
- Step 3 `상세 검증 근거`와 row-level `기술 원문`은 유지한다.
- JSON export는 명시된 auditor/export persona가 없어 V1 범위에서 제외한다.

## Observations

- latest candidate source row는 약 493KB다.
- latest validation row는 약 833KB이며 selection source snapshot을 중복 포함한다.
- current replay raw tab은 session object를 표시하므로 저장 전에는 durable audit record가 아니다.
- actual replay에서 요청 `2016-08-31 → 2026-06-26`, 실제 `2016-08-31 → 2026-06-30`, 공통 가격일 `2026-06-26`, coverage PASS, 제한 종목 COMT/TIP/XLE가 compact record로 투영됐다.
- actual Data Trust internal status `weighted_mix_snapshot`은 사용자 화면에서 `확인 완료`로 번역한다.
