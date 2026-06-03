# Operations Overview IA V1 Risks

| Risk | Mitigation |
| --- | --- |
| Streamlit navigation nesting remains shallow. | Add `Operations Overview` first and keep existing routes. |
| Archive tools still appear in top navigation. | Rename labels and add Overview lane that frames them as Archive/Recovery. |
| UI copy could imply live operations. | Keep no-live approval/order/rebalance boundary visible. |
| Browser QA may be slow because app startup loads many modules. | Use focused compile/tests first, then one browser smoke screenshot. |
