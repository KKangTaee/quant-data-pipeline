# Risks

- 해소: source별 consumed intent id와 focused mock test로 rerun 중복 append를 차단했다.
- 완화: CTA를 header가 아니라 총평 / 4행 해석 뒤에 두고 강점 / 약점과 상세 근거가 아래에 이어지게 했다.
- 해소: selected route와 보류 / 탈락 / 재검토 각각의 route option과 button label을 Python model에서 제공한다.
- 잔여: 과거 non-select 판단을 별도 UI에서 조회해야 한다는 실제 사용자 요구가 생기면 Final Review가 아니라 Operations 전용 Decision History를 별도 설계한다.
