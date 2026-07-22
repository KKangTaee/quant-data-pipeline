# Market Research React Navigation V1 Notes

Status: Complete
Last Updated: 2026-07-22

## Decisions

- header와 family/view navigation 전체를 하나의 React component로 묶는다.
- navigation state owner는 Python에 유지한다.
- component는 validated selection event만 반환한다.
- Today나 module React component에 navigation을 결합하지 않는다.
- current Streamlit navigation은 build-missing fallback으로 유지한다.
- drawer, sticky, module body 변경은 제외한다.
- React event가 현재 view와 다를 때 Python이 query/session state를 먼저 저장하고 `st.rerun()`한다. 다음 run의 payload가 새 canonical view를 반영하므로 URL·본문·iframe 선택 상태가 한 화면에서 일치한다.
- 같은 view event에는 rerun하지 않아 persisted component event와 무한 rerun을 피한다.

## Existing Pattern References

- `app/web/today_react_component.py`
- `app/web/overview/events_react_component.py`
- `app/web/streamlit_components/today_workbench/`
- `app/web/streamlit_components/reference_center_workbench/`

## Preservation

- dirty registry, research bundle, run history와 기존 QA images는 stage하지 않는다.
- Market Research view/module data contracts는 변경하지 않는다.

## Browser QA Findings

- 3개 family와 7개 canonical view의 route·selected state가 일치한다.
- desktop 1280px, compact 760px, mobile 420px 모두 page/frame horizontal overflow가 0이다.
- 420px은 family label 3열, view 2열이며 family 설명은 시각 밀도를 낮추되 접근성 텍스트로 유지한다.
- component 자체 console error는 없었다. `/overview/_stcore/health`, `/overview/_stcore/host-config` 상대 경로 404 두 건은 기존 직접 deep-link server path 이슈다.
