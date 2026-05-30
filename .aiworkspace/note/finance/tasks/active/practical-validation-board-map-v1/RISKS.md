# Risks

- 보드가 너무 많이 표시되면 오히려 UX가 복잡해질 수 있다. 상단 map은 compact table과 badge 중심으로 둔다.
- 조건부 board를 완전히 숨기면 사용자가 왜 없어진지 모를 수 있다. 비적용 board는 collapsed expander로 남긴다.
- saved validation result 중 오래된 row는 board map field가 없을 수 있다. UI helper는 map이 없으면 badge를 생략하고 기존 표시를 유지한다.
