# Market Research React Navigation V1 Notes

Status: Active
Last Updated: 2026-07-22

## Decisions

- header와 family/view navigation 전체를 하나의 React component로 묶는다.
- navigation state owner는 Python에 유지한다.
- component는 validated selection event만 반환한다.
- Today나 module React component에 navigation을 결합하지 않는다.
- current Streamlit navigation은 build-missing fallback으로 유지한다.
- drawer, sticky, module body 변경은 제외한다.

## Existing Pattern References

- `app/web/today_react_component.py`
- `app/web/overview/events_react_component.py`
- `app/web/streamlit_components/today_workbench/`
- `app/web/streamlit_components/reference_center_workbench/`

## Preservation

- dirty registry, research bundle, run history와 기존 QA images는 stage하지 않는다.
- Market Research view/module data contracts는 변경하지 않는다.
