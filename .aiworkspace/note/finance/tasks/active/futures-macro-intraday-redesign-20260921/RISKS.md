# 남은 위험과 구현 시 확인

Date: 2026-09-21

| 위험 | 대응 / 완료 단계 |
|---|---|
| Today/Monitoring 공용 snapshot의 의미 또는 freshness 변경 | current parity, 새 key/read adapter, 실제 consumer 회귀 / 1·5차 |
| 구 full materializer의 대체 진입에서 무거운 연구 재실행 | production caller 전수 참조, collector attach 기본 변경, sentinel / 1차 |
| 월요일/긴 휴장에 2d 자료로 직전 마감 없음 | 저장 coverage 먼저, 누락 종목 bounded 5d/1mo 수집, 불가 시 명시 / 2차 |
| provider bar timestamp·delay가 기대와 다름 | 실제 raw와 완료 시각 점검, 미완료 봉 제외, 공통 endpoint 확인 / 2차 |
| 선물 상품별 정기 중단·휴장과 미국 현물 휴장의 차이 | cash anchor calendar와 각 상품 관측 가용성을 분리, 휴장을 추측하지 않음 / 2차 |
| 일부 통화 결측으로 달러 의미가 바뀜 | 5개 고정 구성, 결측 시 비공개 / 2·3차 |
| 오래된 optional asset이 전체 신호를 막거나 최신으로 섞임 | 필수 집합과 보조 관측 구분, 같은 cutoff 없는 자산의 해석만 제한 / 2·3차 |
| 연속계약 rollover가 가격 변화에 포함 | 현재 공급사 한계 명시; 식별된 불연속을 경제 충격으로 자동 명명하지 않음. 완전한 계약별 roll 보장은 별도 데이터 범위 / 2·3차 |
| 경제적 메커니즘 문장을 단기 방향 확률로 오인 | 관측/해석/연구 상태 분리, 다음 확인 조건과 반대 관측 동시 표시 / 3·4차 |
| 실제 source 응답에 따라 총 갱신 시간이 변함 | 로컬 계산 목표와 provider 시간을 분리 측정; 개선 전 확정 초수 약속 금지 / 5차 |
| 충분한 장중 history 없음 | 이번 완료 조건에서 장중 확률 제외, 별도 연구 요청 시 coverage/protocol부터 시작 |

실제 provider 수집·DB current write·브라우저·회귀를 실행했다. 상세 결과는 RUNS.md에 둔다.

남은 제한:
- provider 응답 지연·누락 및 연속계약 교체는 남는다. 거래소 직접 체결/계약별 roll 보정은 범위 밖이다.
- 개별 선물의 특별 휴일 거래시간은 별도 calendar가 없다. 확인할 수 없는 지연을 정상 휴장으로 숨기지 않는다.
- 장중 역사적 확률은 아직 검증하지 않았으므로 n/N·미래 확률은 공개하지 않는다.
- 원본 master에서도 동일 실패하는 기존 thermometer 계약 테스트 3개가 있다. 이번 변경에서 해당 계산을 수정하지 않았다.
