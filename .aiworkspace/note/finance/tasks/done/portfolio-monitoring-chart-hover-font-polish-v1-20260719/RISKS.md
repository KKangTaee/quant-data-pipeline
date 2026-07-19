# Risks

- 열린 구현 blocker 없음.
- in-app Browser automation은 tall Streamlit iframe의 SVG pointer 좌표 변환을 직접 재현하지 못해 keyboard focus로 visible tooltip을 확인했다. Pointer nearest-point 계산과 `onPointerMove` wiring은 각각 React/Python 계약 테스트로 고정했다.
