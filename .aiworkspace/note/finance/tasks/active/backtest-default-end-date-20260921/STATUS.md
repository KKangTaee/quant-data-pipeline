# 상태

State: complete

- 1차 완료: 공통 설정의 검증 종료일을 생성 시점의 오늘 날짜로 변경. prefill/draft 우선순위 보존.
- 2차 완료: 날짜 전환 시 13개 concrete variant와 입력 보존 테스트, 관련 테스트 91개 통과. 기존 Risk-On payload key 테스트 실패 1개는 변경 전에도 재현되어 RISKS/RUNS에 기록.
- Browser QA: 기본 Quality+Value와 GTAA 새 설정 모두 2026-09-21 확인. 8510 서버 재시작 및 health 정상.
- Python compile, diff check, 독립 코드 리뷰 완료.
- 잔여 차수 없음. 다음 확인 위치: `app/services/backtest_single_settings_workspace.py::_date_fields`.
- 별도 Cash/현금 질문 조사 내용은 NOTES.md에 보관. 보유 표시 수정은 이번 범위에 포함하지 않았다.
