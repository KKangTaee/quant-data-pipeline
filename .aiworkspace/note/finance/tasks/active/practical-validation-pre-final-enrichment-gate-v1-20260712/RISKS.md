# Risks

- provider 일시 장애가 Final Review 승격을 영구 차단하지 않도록 실패 상태와 source mapping 한계를 구분해야 한다.
- 수집 성공만으로 저장 validation이나 Final Review report를 최신으로 간주하면 안 된다.
- legacy saved validation의 audit history를 재작성하거나 삭제하지 않는다.
