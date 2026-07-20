# Notes

- 실제 화면 비교에서 Market Context/Futures Macro는 rounded blue-gray integrated surface와 editorial hierarchy를 사용한다.
- 현재 Market Movers는 white rectangular sheet, small admin typography, native-select appearance, teal/blue/purple competing accents 때문에 prototype처럼 보인다.
- 승인 방향은 Futures Macro의 integrated surface와 Market Context의 reading flow를 결합한 A안이다.
- 기존 payload/event/data 계약은 충분하므로 presentation-only change로 제한한다.
- outer surface는 `20px` radius, `#d8e4ea` border, 145deg blue-gray gradient와 낮은 shadow로 통일했다.
- 상단은 hero/trust -> 탐색 command band -> payload-derived market pulse 순서이며, 운영 진단값은 사용자 질문을 가리지 않는 보조 근거로 유지했다.
- ranking과 breadth는 한 decision row로 묶되 desktop `1.62fr / 1fr`, 900px 이하 single column로 전환한다. 선택/상승/하락 색은 의미 색상으로만 사용하며 purple decorative accent는 제거했다.
- 선택 종목 상세는 `가격·모멘텀 / 재무 / 뉴스·공시` report-family tab을 사용한다. 재무는 `보고 주기`, `재무 영역`, `재무 Factor`를 각각 독립 그룹으로 유지한다.
- 시세 chart는 primary blue, 재무 chart는 trust teal을 사용하고 chart/readout은 desktop `7fr / 3fr`, 작은 화면에서는 single column이다.
- Python service, DB loader, ranking/financial 계산, payload schema와 `set_control`/`select_symbol` event 계약은 변경하지 않았다.
