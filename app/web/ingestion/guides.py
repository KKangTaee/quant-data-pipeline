"""Job guide copy, domains, and labels for Workspace > Ingestion."""

from __future__ import annotations

from typing import Any


JOB_GUIDE: dict[str, dict[str, Any]] = {
    "daily_market_update": {
        "title": "일별 가격 업데이트",
        "purpose": "선택한 운용 universe의 OHLCV, 배당, 분할 가격 이력을 갱신합니다.",
        "targets": ["finance_price.nyse_price_history"],
        "used_by": ["Backtest Analysis", "Data Coverage Audit", "Selected Dashboard symbol freshness"],
        "caveats": [
            "무료 provider no-data와 rate limit이 발생할 수 있습니다.",
            "요청 기간 대비 실제 DB coverage와 최신 거래일을 결과에서 확인해야 합니다.",
        ],
        "next_action": "부분 성공이면 Price Stale Diagnosis로 provider gap과 DB 수집 누락을 분리하세요.",
    },
    "weekly_fundamental_refresh": {
        "title": "Archived legacy broad yfinance fundamentals / factors",
        "purpose": (
            "Archived legacy broad yfinance compatibility path for historical nyse_fundamentals / nyse_factors replay; "
            "not an active financial statement refresh workflow."
        ),
        "targets": ["finance_fundamental.nyse_fundamentals", "finance_fundamental.nyse_factors"],
        "used_by": ["Old run history replay", "explicit legacy broad factor comparison"],
        "caveats": [
            "broad fundamentals / factors는 strict filing-time PIT source가 아닙니다.",
            "strict annual backtests use EDGAR statement shadow.",
        ],
        "next_action": "새 financial statement coverage가 필요하면 EDGAR 재무제표 갱신을 먼저 실행하세요.",
    },
    "extended_statement_refresh": {
        "title": "EDGAR 재무제표 갱신",
        "purpose": (
            "EDGAR detailed annual / quarterly statement ledger를 수집하고 statement shadow fundamentals / factors를 재구성하는 "
            "primary financial statement refresh입니다."
        ),
        "targets": [
            "finance_fundamental.nyse_financial_statement_filings",
            "finance_fundamental.nyse_financial_statement_values",
            "finance_fundamental.nyse_fundamentals_statement",
            "finance_fundamental.nyse_factors_statement",
        ],
        "used_by": ["Strict annual factor runtime", "Market Movers financial snapshot", "Statement PIT inspection"],
        "caveats": [
            "period_end와 accepted_at / available_at를 구분해서 해석해야 합니다.",
            "SEC fair access를 위해 User-Agent와 pacing을 지켜야 합니다.",
        ],
        "next_action": "부분 성공이면 Statement Coverage Diagnosis로 raw 누락과 shadow rebuild 대상을 분리하세요.",
    },
    "metadata_refresh": {
        "title": "종목 메타데이터 업데이트",
        "purpose": "현재 NYSE stock / ETF universe의 asset profile과 ETF current-operability bridge fields를 갱신합니다.",
        "targets": ["finance_meta.nyse_asset_profile"],
        "used_by": ["Universe filter", "ETF operability bridge", "Overview Top1000 / Top2000 universe"],
        "caveats": ["asset profile은 current snapshot이며 historical universe proof가 아닙니다."],
        "next_action": "Profile filter 결과가 달라졌다면 가격 / provider snapshot도 이어서 갱신하세요.",
    },
    "collect_fomc_calendar": {
        "title": "FOMC 일정 수집",
        "purpose": "Federal Reserve 공식 calendar에서 FOMC meeting 일정을 수집합니다.",
        "targets": ["finance_meta.market_event_calendar"],
        "used_by": ["Workspace > Overview > Events"],
        "caveats": ["event row는 수집 시점의 calendar snapshot입니다."],
        "next_action": "Overview Events에서 일정 fresh 상태를 확인하세요.",
    },
    "collect_macro_calendar": {
        "title": "공식 매크로 발표 일정 수집",
        "purpose": "BLS / BEA 공식 release schedule에서 CPI, PPI, Jobs, GDP 발표 일정을 수집합니다.",
        "targets": ["finance_meta.market_event_calendar"],
        "used_by": ["Workspace > Overview > Events"],
        "caveats": ["BLS 자동 요청은 차단될 수 있으며, 실패 시 BLS .ics import를 사용합니다."],
        "next_action": "partial_success면 실패 source를 확인하고 BLS .ics fallback을 실행하세요.",
    },
    "collect_market_structure_calendar": {
        "title": "시장 구조 일정 수집",
        "purpose": "Nasdaq Trader / Cboe / FTSE Russell calendar에서 휴장, 조기폐장, options expiration, Russell reconstitution 일정을 수집합니다.",
        "targets": ["finance_meta.market_event_calendar"],
        "used_by": ["Workspace > Overview > Events"],
        "caveats": ["일정 밀도와 자료 상태 근거이며 매매 신호나 monitoring action이 아닙니다."],
        "next_action": "partial_success면 실패 source를 확인하고 성공 row만 Events에서 먼저 확인하세요.",
    },
    "import_bls_macro_calendar_ics": {
        "title": "BLS 공식 .ics 일정 가져오기",
        "purpose": "브라우저로 받은 BLS 공식 calendar 파일에서 CPI / PPI / Jobs 발표 일정을 가져옵니다.",
        "targets": ["finance_meta.market_event_calendar"],
        "used_by": ["Workspace > Overview > Events"],
        "caveats": ["업로드한 파일의 source year 범위와 최신성을 확인해야 합니다."],
        "next_action": "Overview Events에서 BLS row가 보강됐는지 확인하세요.",
    },
    "collect_earnings_calendar": {
        "title": "실적 발표 예상 일정 수집",
        "purpose": "bounded symbol set의 upcoming earnings estimate를 yfinance와 선택적 Nasdaq cross-check로 수집합니다.",
        "targets": ["finance_meta.market_event_calendar"],
        "used_by": ["Workspace > Overview > Events"],
        "caveats": ["무료 provider estimate이며 공식 확정 IR 일정이 아닙니다."],
        "next_action": "missing / failed symbol은 Earnings Diagnostics에서 reason을 확인하세요.",
    },
    "collect_futures_ohlcv": {
        "title": "선물 1분봉 OHLCV 수집",
        "purpose": "Overview Futures Monitor에서 읽을 주요 선물 OHLCV 캔들을 yfinance pilot source로 수집합니다.",
        "targets": [
            "finance_price.futures_ohlcv",
            "finance_meta.futures_instrument",
            "finance_meta.futures_market_monitor_run",
        ],
        "used_by": ["Workspace > Overview > Futures Monitor", "Workspace > Overview > Data Health"],
        "caveats": [
            "무료 provider pilot source이며 exchange-grade realtime feed가 아닙니다.",
            "provider 실패 / stale 상태는 Overview에서 그대로 표시합니다.",
        ],
        "next_action": "부분 성공이면 failed symbols를 줄여 다시 실행하거나 provider 상태를 확인하세요.",
    },
    "collect_market_sentiment": {
        "title": "시장 심리 수집",
        "purpose": "CNN Fear & Greed와 AAII Sentiment Survey를 수집해 Overview Sentiment에서 읽을 시장 심리 context를 저장합니다.",
        "targets": ["finance_meta.macro_series_observation"],
        "used_by": ["Workspace > Overview > Sentiment", "Workspace > Overview > Data Health"],
        "caveats": [
            "시장 심리는 trade signal이나 live approval이 아닙니다.",
            "CNN / AAII source 차단 또는 stale 상태는 Overview에서 그대로 표시합니다.",
        ],
        "next_action": "partial_success이면 failed source를 확인하고 다시 실행하세요.",
    },
    "discover_etf_provider_source_map": {
        "title": "ETF 공식 소스 매핑 발견",
        "purpose": "ETF별 공식 운용사 endpoint와 parser mapping을 찾아 verified cache로 저장합니다.",
        "targets": ["finance_meta.etf_provider_source_map"],
        "used_by": ["ETF operability / holdings / exposure collection", "Provider Data Gaps"],
        "caveats": ["provider 사이트 구조가 바뀌면 verified row도 다시 확인해야 합니다."],
        "next_action": "verified row가 부족하면 ETF provider connector 보강 후보로 기록하세요.",
    },
    "collect_etf_operability_provider": {
        "title": "ETF 운용성 스냅샷 수집",
        "purpose": "ETF 비용, 규모, 유동성, spread, premium/discount 관련 snapshot을 수집합니다.",
        "targets": ["finance_meta.etf_operability_snapshot"],
        "used_by": ["Practical Validation operability / cost / liquidity"],
        "caveats": ["current snapshot이며 과거 특정 시점의 PIT 운용성 truth가 아닙니다."],
        "next_action": "coverage gap이 있으면 source map 또는 DB bridge 수집 경로를 확인하세요.",
    },
    "collect_etf_holdings_exposure": {
        "title": "ETF 구성 / 노출 스냅샷 수집",
        "purpose": "ETF holdings row와 asset / sector / country / currency exposure summary를 수집합니다.",
        "targets": ["finance_meta.etf_holdings_snapshot", "finance_meta.etf_exposure_snapshot"],
        "used_by": ["Practical Validation asset allocation / concentration / overlap"],
        "caveats": ["current holdings snapshot이며 과거 holdings PIT truth가 아닙니다."],
        "next_action": "partial_success이면 unsupported parser와 missing ETF를 먼저 확인하세요.",
    },
    "collect_macro_market_context": {
        "title": "FRED 시장환경 수집",
        "purpose": "VIX, yield curve, credit spread 같은 validation용 market-context series를 수집합니다.",
        "targets": ["finance_meta.macro_series_observation"],
        "used_by": ["Practical Validation macro / regime / risk-on-off diagnostics"],
        "caveats": ["FRED observation date 기준이며 ALFRED vintage PIT는 아닙니다."],
        "next_action": "Macro freshness가 stale이면 동일 series와 기간으로 다시 수집하세요.",
    },
    "collect_sec_form25_delistings": {
        "title": "SEC Form 25 상폐 근거 수집",
        "purpose": "SEC EDGAR Form 25 / 25-NSE filing metadata로 delisting evidence를 저장합니다.",
        "targets": ["finance_meta.nyse_symbol_lifecycle"],
        "used_by": ["Data Coverage Audit survivorship / delisting control"],
        "caveats": ["Form 25 부재는 active listing proof가 아닙니다."],
        "next_action": "unmapped / no Form 25 symbol은 별도 historical listing source가 필요한지 검토하세요.",
    },
    "collect_symbol_directory_snapshots": {
        "title": "Nasdaq 상장 관찰치 수집",
        "purpose": "Nasdaq public Symbol Directory current files를 partial listing_observed evidence로 저장합니다.",
        "targets": ["finance_meta.nyse_symbol_lifecycle"],
        "used_by": ["Data Coverage Audit lifecycle evidence"],
        "caveats": ["current listing snapshot이며 historical membership PASS 근거가 아닙니다."],
        "next_action": "반복 관찰이 쌓이면 computed lifecycle 요약을 실행하세요.",
    },
    "collect_sec_company_ticker_crosscheck": {
        "title": "SEC CIK / 티커 교차확인",
        "purpose": "SEC current CIK / ticker / exchange association을 identity cross-check evidence로 저장합니다.",
        "targets": ["finance_meta.nyse_symbol_lifecycle"],
        "used_by": ["Data Coverage Audit lifecycle evidence"],
        "caveats": ["current identity row이며 delisting이나 historical membership proof가 아닙니다."],
        "next_action": "requested missing symbol은 SEC ticker mapping 한계를 따로 확인하세요.",
    },
    "collect_computed_snapshot_lifecycle": {
        "title": "반복 관찰 lifecycle 요약",
        "purpose": "기존 current snapshot rows의 반복 관찰 window를 보수적인 partial lifecycle evidence로 요약합니다.",
        "targets": ["finance_meta.nyse_symbol_lifecycle"],
        "used_by": ["Data Coverage Audit lifecycle evidence"],
        "caveats": ["absence를 delisting proof로 해석하지 않으며 PASS eligible evidence가 아닙니다."],
        "next_action": "actual historical membership source가 필요한 symbol은 별도 source review로 넘기세요.",
    },
    "pipeline_core_market_data": {
        "title": "Archived broad core market-data pipeline",
        "purpose": "Archived legacy compatibility job that chained OHLCV, broad yfinance fundamentals, and broad factor calculation.",
        "targets": ["finance_price.nyse_price_history", "finance_fundamental.nyse_fundamentals", "finance_fundamental.nyse_factors"],
        "used_by": ["Old run history replay", "explicit legacy broad factor comparison"],
        "caveats": ["financial statement canonical refresh는 EDGAR annual path입니다."],
        "next_action": "새 재무제표 / factor 준비는 EDGAR refresh와 statement shadow path를 사용하세요.",
    },
    "collect_ohlcv": {
        "title": "가격 이력 수동 수집",
        "purpose": "선택한 symbol과 기간의 OHLCV, dividend, split row를 수동으로 수집합니다.",
        "targets": ["finance_price.nyse_price_history"],
        "used_by": ["Backtest Analysis", "freshness diagnostics"],
        "caveats": ["요청 범위와 실제 provider 응답 범위가 다를 수 있습니다."],
        "next_action": "누락 symbol은 Price Stale Diagnosis로 원인을 분류하세요.",
    },
    "diagnose_price_stale": {
        "title": "가격 stale 원인 진단",
        "purpose": "DB latest date, provider probe, asset profile 상태를 읽어 가격 stale 원인을 분리합니다.",
        "targets": ["finance_price.nyse_price_history", "finance_meta.nyse_asset_profile"],
        "used_by": ["Manual recovery", "Data Coverage Audit", "Price Freshness Preflight"],
        "caveats": ["읽기 전용 진단이며 새 가격 row를 저장하지 않습니다."],
        "next_action": "local ingestion gap이면 가격 이력 수동 수집으로 기간을 좁혀 보강하세요.",
    },
    "diagnose_statement_universe_coverage": {
        "title": "재무제표 universe coverage QA",
        "purpose": "Top1000 / Top2000 / Nasdaq 등 universe 단위로 EDGAR statement coverage 원인을 점검합니다.",
        "targets": [
            "finance_fundamental.nyse_financial_statement_values",
            "finance_fundamental.nyse_fundamentals_statement",
            "finance_fundamental.nyse_factors_statement",
        ],
        "used_by": ["Strict statement coverage review", "Statement recovery planning"],
        "caveats": ["읽기 전용 QA이며 paid provider나 yfinance statement data를 primary source로 읽지 않습니다."],
        "next_action": "raw present / shadow missing이면 shadow rebuild, raw missing이면 EDGAR refresh로 분리하세요.",
    },
    "diagnose_statement_coverage": {
        "title": "재무제표 coverage 원인 진단",
        "purpose": "선택 symbol의 raw statement, shadow table, live EDGAR sample 상태를 비교합니다.",
        "targets": [
            "finance_fundamental.nyse_financial_statement_values",
            "finance_fundamental.nyse_fundamentals_statement",
        ],
        "used_by": ["Manual statement recovery", "PIT inspection"],
        "caveats": ["읽기 전용 진단이며 EDGAR sample 조회는 source shape 확인 목적입니다."],
        "next_action": "source-present raw-missing이면 EDGAR refresh, raw-present shadow-missing이면 shadow rebuild를 실행하세요.",
    },
    "inspect_statement_pit": {
        "title": "재무제표 PIT inspection",
        "purpose": "저장된 statement timing row와 EDGAR source payload shape를 UI에서 점검합니다.",
        "targets": [
            "finance_fundamental.nyse_financial_statement_values",
            "finance_fundamental.nyse_fundamentals_statement",
        ],
        "used_by": ["Point-in-time validation", "Statement source review"],
        "caveats": ["읽기 전용 inspection이며 live source sample은 대표 payload 확인용입니다."],
        "next_action": "accepted_at / available_at 의미가 어긋나면 factor PIT 변환 경계를 먼저 점검하세요.",
    },
    "collect_fundamentals": {
        "title": "Archived broad fundamentals manual collection",
        "purpose": "Archived legacy compatibility job for broad yfinance normalized fundamentals.",
        "targets": ["finance_fundamental.nyse_fundamentals"],
        "used_by": ["Old run history replay", "explicit legacy broad factor comparison"],
        "caveats": ["canonical financial statement source가 아닙니다."],
        "next_action": "새 재무제표 source가 필요하면 EDGAR refresh를 사용하세요.",
    },
    "calculate_factors": {
        "title": "Archived broad factor manual calculation",
        "purpose": "Archived legacy compatibility job for calculating broad factors from nyse_fundamentals.",
        "targets": ["finance_fundamental.nyse_factors"],
        "used_by": ["Old run history replay", "explicit legacy broad factor comparison"],
        "caveats": ["strict annual strategies use statement shadow factors."],
        "next_action": "새 factor 준비는 statement shadow factor path를 우선 사용하세요.",
    },
    "collect_asset_profiles": {
        "title": "자산 프로필 수동 수집",
        "purpose": "NYSE universe table을 기준으로 stock / ETF profile metadata를 수집합니다.",
        "targets": ["finance_meta.nyse_asset_profile"],
        "used_by": ["Universe filter", "metadata refresh"],
        "caveats": ["current profile snapshot입니다."],
        "next_action": "profile table이 비어 있으면 NYSE universe 적재 상태부터 확인하세요.",
    },
    "collect_financial_statements": {
        "title": "상세 재무제표 수동 수집",
        "purpose": "선택한 symbol의 EDGAR detailed statement raw ledger를 수집합니다.",
        "targets": [
            "finance_fundamental.nyse_financial_statement_filings",
            "finance_fundamental.nyse_financial_statement_values",
            "finance_fundamental.nyse_financial_statement_labels",
        ],
        "used_by": ["Statement shadow rebuild", "PIT inspection"],
        "caveats": ["issuer별 form 구조와 concept coverage가 다를 수 있습니다."],
        "next_action": "routine strict coverage 복구는 Extended Statement Refresh를 우선 사용하세요.",
    },
    "rebuild_statement_shadow": {
        "title": "재무제표 shadow 재구성",
        "purpose": "이미 저장된 raw statement ledger로 statement fundamentals / factors shadow를 재구성합니다.",
        "targets": ["finance_fundamental.nyse_fundamentals_statement", "finance_fundamental.nyse_factors_statement"],
        "used_by": ["Strict annual / quarterly factor runtime"],
        "caveats": ["raw statement rows가 없으면 shadow row도 생성되지 않습니다."],
        "next_action": "raw present / shadow missing이면 이 job, raw missing이면 Extended Statement Refresh를 실행하세요.",
    },
}

PRICE_COLLECTION_JOBS = {"daily_market_update", "collect_ohlcv"}
COMPOSITE_PRICE_JOBS = {"pipeline_core_market_data"}
LIFECYCLE_EVIDENCE_JOBS = {
    "collect_sec_form25_delistings",
    "collect_symbol_directory_snapshots",
    "collect_sec_company_ticker_crosscheck",
    "collect_computed_snapshot_lifecycle",
}
PARTIAL_LIFECYCLE_EVIDENCE_JOBS = {
    "collect_symbol_directory_snapshots",
    "collect_sec_company_ticker_crosscheck",
    "collect_computed_snapshot_lifecycle",
}
ETF_PROVIDER_JOBS = {
    "discover_etf_provider_source_map",
    "collect_etf_operability_provider",
    "collect_etf_holdings_exposure",
}
EVENT_CALENDAR_JOBS = {
    "collect_fomc_calendar",
    "collect_macro_calendar",
    "collect_market_structure_calendar",
    "import_bls_macro_calendar_ics",
    "collect_earnings_calendar",
}
MACRO_CONTEXT_JOBS = {"collect_macro_market_context", "collect_market_sentiment"}
DIAGNOSTIC_PROGRESS_JOBS = {
    "diagnose_price_stale",
    "diagnose_statement_universe_coverage",
    "diagnose_statement_coverage",
    "inspect_statement_pit",
}
PROGRESS_ENABLED_ACTIONS = (
    PRICE_COLLECTION_JOBS
    | COMPOSITE_PRICE_JOBS
    | LIFECYCLE_EVIDENCE_JOBS
    | ETF_PROVIDER_JOBS
    | EVENT_CALENDAR_JOBS
    | MACRO_CONTEXT_JOBS
    | DIAGNOSTIC_PROGRESS_JOBS
    | {
        "weekly_fundamental_refresh",
        "extended_statement_refresh",
        "rebuild_statement_shadow",
        "collect_financial_statements",
        "collect_futures_ohlcv",
        "metadata_refresh",
        "collect_asset_profiles",
    }
)


def _job_domain(job_name: str | None) -> str:
    normalized = str(job_name or "")
    if normalized in PRICE_COLLECTION_JOBS:
        return "price"
    if normalized in COMPOSITE_PRICE_JOBS:
        return "pipeline"
    if normalized in LIFECYCLE_EVIDENCE_JOBS:
        return "lifecycle"
    if normalized in ETF_PROVIDER_JOBS:
        return "provider"
    if normalized in MACRO_CONTEXT_JOBS:
        return "macro"
    if normalized in EVENT_CALENDAR_JOBS:
        return "event"
    if "statement" in normalized:
        return "statement"
    if "fundamental" in normalized or "factor" in normalized:
        return "fundamental"
    if "profile" in normalized or "metadata" in normalized:
        return "metadata"
    return "generic"


def _result_metric_labels(job_name: str | None) -> tuple[str, str, str, str, str]:
    domain = _job_domain(job_name)
    if domain == "lifecycle":
        return ("상태", "증거 Row", "관찰 / 요청", "누락 Source/Symbol", "소요 시간(초)")
    if domain in {"provider", "macro", "event"}:
        return ("상태", "저장 Row", "수집 대상", "누락 / 실패", "소요 시간(초)")
    if domain == "price":
        return ("상태", "가격 Row", "요청 Symbol", "누락 / 실패", "소요 시간(초)")
    if domain == "pipeline":
        return ("상태", "총 저장 Row", "요청 Symbol", "누락 / 실패", "소요 시간(초)")
    return ("상태", "저장 Row", "요청 대상", "누락 / 실패", "소요 시간(초)")


def _job_guide(job_name: str | None) -> dict[str, Any]:
    return JOB_GUIDE.get(str(job_name or ""), {})


def _job_title(job_name: str | None) -> str:
    guide = _job_guide(job_name)
    return str(guide.get("title") or job_name or "-")


def _status_label(status: str | None) -> str:
    return {
        "success": "성공",
        "partial_success": "부분 성공",
        "failed": "실패",
    }.get(str(status or ""), str(status or "-"))
