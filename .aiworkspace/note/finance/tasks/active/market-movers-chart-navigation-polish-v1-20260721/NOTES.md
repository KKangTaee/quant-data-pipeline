# Notes

Last Updated: 2026-07-21

- 사용자 첨부 화면에서 재무 39개 분기가 고정 720 viewBox에 압축되고 X축은 양 끝 날짜만 보였다.
- 가격 readout의 의미 색상은 유지하되 배경 tint와 `is-primary` 좌측 강조선은 제거한다.
- 새 chart dependency는 추가하지 않고 기존 SVG helper를 확장한다.
- 분기는 point당 58px, 연간은 point당 72px의 intrinsic width를 사용하고 viewport보다 작을 때는 100%로 확장한다.
- factor/symbol research가 바뀌면 active hover를 초기화하고 최신 기간이 보이도록 오른쪽 끝으로 정렬한다.
- pointer drag는 scroll viewport가 소유하고 SVG는 exact nearest point hover와 좌우/Home/End keyboard 이동을 소유한다.
