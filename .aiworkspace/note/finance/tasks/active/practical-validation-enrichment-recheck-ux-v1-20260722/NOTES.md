# Notes

- 수집 후 replay 초기화와 save-and-move guard는 올바른 안전장치다.
- 회귀는 provider/validation 기능이 아니라 one-shell의 lifecycle projection 누락이다.
- `build_practical_validation_recovery_progress()`와 enrichment session state는 남아 있지만 current render path에서 소비되지 않는다.
- 현재 notice는 내용과 관계없이 `st.success()`로 렌더링된다.
- 수집과 replay는 명시적 두 작업으로 유지하고 같은 화면에서 다음 CTA를 연결한다.
- Decision Workspace가 source별 progress와 collection results를 받아 `recheck_required / blocked / save_ready` lifecycle을 투영한다.
- collector status는 성공, 확인 필요, 실패로 보수적으로 집계하며 unknown/partial을 전체 성공으로 올리지 않는다.
- React와 Streamlit fallback은 같은 read model을 읽고, raw job/row table 대신 현재 단계와 다음 행동만 first-read에 표시한다.
- actual fixture에서 `보강된 데이터로 재검증` 클릭 후 replay PASS와 Gate eligible을 받아 `새 결과 저장` current, `Final Review` next로 전환됨을 확인했다.
