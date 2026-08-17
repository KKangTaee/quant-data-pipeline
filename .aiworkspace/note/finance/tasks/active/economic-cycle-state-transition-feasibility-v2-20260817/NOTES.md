# Notes

## 2026-08-17 Product Contract Reset

- fixed adjacent monitor는 forecast가 아니다.
- RTDSM-only model은 current state 연구에는 유효하지만 원래 transition mechanism을
  충분히 설명하지 못한다.
- extended model은 policy/inflation/rates/credit를 required driver group으로 검증한다.
- market prices는 optional shadow block이며 기존 자산별 확인 포인트와 계산 경계를
  공유하지 않는다.
- fiscal policy는 현재 승인된 long PIT source가 없으므로 heuristic flag를 만들지 않는다.
