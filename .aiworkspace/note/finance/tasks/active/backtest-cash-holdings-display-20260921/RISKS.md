# 경계와 검증 제한

- 리밸런싱 날짜의 중간 평가행 포함 문제는 별도 계산 이슈로 이번 표시 수정에 포함하지 않는다.
- 독립 리뷰 3개 finding 모두 수정, 최종 추가 finding 없음.
- 관련 Python 38개 및 Vite production build 통과. standalone TypeScript 검사는 기존 React 타입 누락/Node 타입 충돌 때문에 전체 pass가 아니며 HEAD 격리 재현도 같은 원인으로 실패했다. RUNS 참조.
- 전후 ticker 계약이 다른 전략은 변경 전을 추정하지 않는다. 변경 후·현금·명시적 매매 기록은 보존한다.
- 사용자 변경 registry 2개 및 기존 미추적 산출물 보존. 생성 스크린샷/QA script/run evidence는 /tmp에만 보존하고 커밋하지 않는다.
