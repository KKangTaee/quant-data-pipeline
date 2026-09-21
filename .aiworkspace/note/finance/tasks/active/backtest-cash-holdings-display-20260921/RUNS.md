# 검증

- 신규 회귀 테스트 6개 모두 기존 오류로 실패(RED) 확인.
- 수정 후 결과 workspace 테스트 34개 통과. 기존 edgar deprecation warning 3개.
- 리뷰에서 발견한 투자분 내부 정규화 Next Weight/명시 Added·Removed 보존 2개 회귀를 RED 확인 후 수정. 36개 통과.
- GRS/strict 등 전후 ticker 계약 차이는 리밸런싱 전 표시를 확인 불가로 제한해 허위 구성을 차단. 관련 2개 포함 최종 38개 통과.
- 프런트엔드 `npm run build` 성공. 배포용 component_static 갱신.
- 별도 `tsc --noEmit`는 React/React DOM 타입 누락과 기존 Node 타입 충돌로 실패. HEAD 소스 격리 재현도 같은 TS7016/TS7026/TS2430/TS2344/TS2403/TS2386 유형으로 실패(329/331개; 추가 JSX 문구 2개에 같은 누락 타입 오류). 결과 로그 /tmp/cash-ui-tsc-{baseline,current}.log.
- 실제 DB 동일 GTAA 설정 129행 재계산: 평가 가능한 전후 비중 합계 오류 0. 마지막 변경 후 SOXX 50%, MTUM 50%, 현금 0. /tmp/gtaa-cash-live-verification.json.
- 실제 React component를 별도 로컬 Streamlit QA fixture로 검증: 전액 현금 전환/부분 현금/현금에서 두 종목 매수 모두 전후 카드 정확. 사용자용 표는 현금 100%, 제외 SOXX·MTUM으로 표시. screenshot /tmp/gtaa-cash-holdings-table-20260921.png (generated, 커밋 제외).
- py_compile, git diff --check 통과.
- 독립 최종 리뷰: 추가 actionable finding 없음. 8510 서버 PID 46568 재시작, /_stcore/health ok.
