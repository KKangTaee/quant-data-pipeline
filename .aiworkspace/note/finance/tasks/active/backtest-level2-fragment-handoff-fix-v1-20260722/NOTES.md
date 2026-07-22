# Notes

- 실제 재현에서 React `setComponentValue`와 Python handler는 정상 동작했다.
- 문제는 handler 이후 full-app rerun 승격이 아니라 fragment callback rerun으로 끝나는 경계다.
- latest GTAA history row는 selection source 변환이 가능한 정상 계약이었다.
- 저장 handler와 route owner는 유지하고 intent 소비 시점만 옮긴다.
