# 설계

`_date_fields()`에서 `date.today().isoformat()`을 사용해 날짜가 앱 시작 시점에 고정되지 않게 한다. 기존 supplied values 및 prefill/draft 우선순위를 유지한다. 전략 계산, 거래일 보정, 기존 사용자 세션의 날짜는 변경하지 않는다.
