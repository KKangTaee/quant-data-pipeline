# finance/data/db/schema.py

import re
from typing import Dict, List, Tuple


def _parse_table_name(create_table_sql: str) -> str:
    """CREATE TABLE SQL에서 테이블명 추출"""
    match = re.search(r'CREATE TABLE (?:IF NOT EXISTS )?`?(\w+)`?', create_table_sql, re.IGNORECASE)
    if match:
        return match.group(1)
    raise ValueError("테이블명을 찾을 수 없습니다.")


def _parse_columns_from_schema(create_table_sql: str) -> List[Tuple[str, str]]:
    """
    CREATE TABLE SQL에서 컬럼 정의 추출
    Returns: [(column_name, full_column_definition), ...]
    """
    # CREATE TABLE ... ( ... ) 부분 추출
    match = re.search(r'CREATE TABLE[^(]*\((.*)\)', create_table_sql, re.DOTALL | re.IGNORECASE)
    if not match:
        return []

    table_body = match.group(1)
    columns: List[Tuple[str, str]] = []

    # ENUM/함수 인자 내부 콤마를 안전하게 처리하기 위해 top-level 콤마 기준으로 분해
    chunks: List[str] = []
    cur: List[str] = []
    depth = 0
    in_single = False
    in_double = False
    escaped = False

    for ch in table_body:
        if escaped:
            cur.append(ch)
            escaped = False
            continue

        if ch == "\\":
            cur.append(ch)
            escaped = True
            continue

        if ch == "'" and not in_double:
            in_single = not in_single
            cur.append(ch)
            continue

        if ch == '"' and not in_single:
            in_double = not in_double
            cur.append(ch)
            continue

        if not in_single and not in_double:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth = max(0, depth - 1)
            elif ch == "," and depth == 0:
                chunks.append("".join(cur).strip())
                cur = []
                continue

        cur.append(ch)

    if cur:
        chunks.append("".join(cur).strip())

    for chunk in chunks:
        line = chunk.strip()
        if not line or line.startswith("--"):
            continue

        # KEY, PRIMARY KEY, UNIQUE KEY, FOREIGN KEY 등은 제외
        if re.match(r'^\s*(PRIMARY\s+KEY|UNIQUE\s+KEY|KEY|FOREIGN\s+KEY|INDEX|CONSTRAINT)', line, re.IGNORECASE):
            continue

        # 컬럼 정의 파싱 (첫 토큰이 컬럼명)
        column_match = re.match(r'^`?(\w+)`?\s+(.+)$', line, re.IGNORECASE | re.DOTALL)
        if column_match:
            column_name = column_match.group(1)
            column_def = column_match.group(2).strip().rstrip(',')
            columns.append((column_name, column_def))

    return columns


def sync_table_schema(db, table_name: str, create_table_sql: str, db_name: str) -> None:
    """
    스키마 정의와 실제 테이블을 비교하여 누락된 컬럼을 자동 추가
    
    Args:
        db: MySQLClient 인스턴스
        table_name: 테이블명
        create_table_sql: CREATE TABLE SQL 문
        db_name: 데이터베이스명
    """
    # 테이블이 존재하는지 확인
    result = db.query("""
        SELECT COUNT(*) as cnt 
        FROM information_schema.TABLES 
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
    """, (db_name, table_name))
    
    if result[0]["cnt"] == 0:
        # 테이블이 없으면 CREATE TABLE 실행
        db.execute(create_table_sql)
        return
    
    # 스키마에서 컬럼 정의 추출
    schema_columns = _parse_columns_from_schema(create_table_sql)
    schema_column_names = {col[0].lower() for col in schema_columns}
    
    # 실제 테이블의 컬럼 목록 조회
    existing_columns = db.query("""
        SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT, EXTRA
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
        ORDER BY ORDINAL_POSITION
    """, (db_name, table_name))
    
    existing_column_names = {col["COLUMN_NAME"].lower() for col in existing_columns}
    
    # 스키마에는 있지만 테이블에 없는 컬럼 찾기
    missing_columns = []
    for col_name, col_def in schema_columns:
        if col_name.lower() not in existing_column_names:
            missing_columns.append((col_name, col_def))
    
    # 누락된 컬럼 추가
    if missing_columns:
        # 컬럼의 위치를 결정하기 위해 기존 컬럼 순서 확인
        existing_col_list = [col["COLUMN_NAME"] for col in existing_columns]
        
        for col_name, col_def in missing_columns:
            # AFTER 절 결정: 이전 컬럼 찾기
            after_clause = ""
            col_idx = None
            for i, (schema_col_name, _) in enumerate(schema_columns):
                if schema_col_name.lower() == col_name.lower():
                    col_idx = i
                    break
            
            if col_idx is not None and col_idx > 0:
                # 이전 컬럼 찾기
                prev_col = schema_columns[col_idx - 1][0]
                if prev_col.lower() in existing_column_names:
                    after_clause = f"AFTER `{prev_col}`"
                elif existing_col_list:
                    # 이전 컬럼이 없으면 마지막에 추가
                    after_clause = f"AFTER `{existing_col_list[-1]}`"
            
            # ALTER TABLE 실행
            alter_sql = f"ALTER TABLE `{table_name}` ADD COLUMN `{col_name}` {col_def}"
            if after_clause:
                alter_sql += f" {after_clause}"
            
            try:
                db.execute(alter_sql)
                print(f"✅ 컬럼 추가: {table_name}.{col_name}")
            except Exception as e:
                print(f"⚠️  컬럼 추가 실패: {table_name}.{col_name} - {e}")



NYSE_SCHEMAS = {
    "stock": """
        CREATE TABLE IF NOT EXISTS nyse_stock (
            id     BIGINT AUTO_INCREMENT PRIMARY KEY,
            symbol VARCHAR(20) NOT NULL,
            name   VARCHAR(255) NOT NULL,
            url    VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            UNIQUE KEY uk_nyse_stock_symbol (symbol)
        );
    """,

    "etf": """
        CREATE TABLE IF NOT EXISTS nyse_etf (
            id     BIGINT AUTO_INCREMENT PRIMARY KEY,
            symbol VARCHAR(20) NOT NULL,
            name   VARCHAR(255) NOT NULL,
            url    VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            UNIQUE KEY uk_nyse_etf_symbol (symbol)
        );
    """,

    "symbol_lifecycle": """
        CREATE TABLE IF NOT EXISTS nyse_symbol_lifecycle (
          id BIGINT AUTO_INCREMENT PRIMARY KEY,

          symbol VARCHAR(20) NOT NULL,
          kind ENUM('stock','etf') NOT NULL,

          listing_status ENUM('active','inactive','delisted','not_found','unknown','error') NOT NULL DEFAULT 'unknown',
          source VARCHAR(64) NOT NULL,
          source_type ENUM('current_listing_snapshot','historical_listing','delisting_feed','asset_profile_bridge','computed_from_snapshots') NOT NULL DEFAULT 'current_listing_snapshot',
          coverage_status ENUM('actual','partial','bridge','proxy','missing','error') NOT NULL DEFAULT 'partial',

          first_seen_date DATE NULL,
          last_seen_date DATE NULL,
          inactive_detected_at DATE NULL,
          event_type ENUM('listing_observed','historical_membership','delisting','ticker_change','merger','name_change','unknown','error') NOT NULL DEFAULT 'unknown',
          event_date DATE NULL,
          related_symbol VARCHAR(20) NULL,
          related_cik BIGINT NULL,
          resolution_status ENUM('candidate','active','rejected','unknown') NOT NULL DEFAULT 'unknown',
          confidence DOUBLE NULL,

          name VARCHAR(255) NULL,
          source_ref VARCHAR(1024) NULL,
          evidence_json JSON NULL,
          collected_at TIMESTAMP NULL,
          error_msg TEXT NULL,

          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

          UNIQUE KEY uk_symbol_kind_source (symbol, kind, source),
          KEY ix_symbol_kind (symbol, kind),
          KEY ix_source_type (source_type),
          KEY ix_listing_status (listing_status),
          KEY ix_event_type (event_type),
          KEY ix_resolution_status (resolution_status),
          KEY ix_event_date (event_date),
          KEY ix_lifecycle_dates (first_seen_date, last_seen_date)
        );
    """,
    
     "asset_profile": """
        CREATE TABLE IF NOT EXISTS nyse_asset_profile (
          id BIGINT AUTO_INCREMENT PRIMARY KEY,
          symbol VARCHAR(20) NOT NULL,
          kind   ENUM('stock','etf') NOT NULL,

          long_name VARCHAR(255) NULL,
          quote_type VARCHAR(20) NULL,
          exchange VARCHAR(20) NULL,

          sector   VARCHAR(100) NULL,
          industry VARCHAR(150) NULL,
          country  VARCHAR(50)  NULL,
          fund_family VARCHAR(255) NULL,

          market_cap BIGINT NULL,
          total_assets DOUBLE NULL,
          dividend_yield DOUBLE NULL,
          payout_ratio   DOUBLE NULL,
          bid DOUBLE NULL,
          ask DOUBLE NULL,
          bid_size BIGINT NULL,
          ask_size BIGINT NULL,

          is_spac TINYINT(1) NULL,

          status ENUM('active','delisted','not_found','error') NOT NULL DEFAULT 'active',
          last_collected_at TIMESTAMP NULL,
          delisted_at       TIMESTAMP NULL,
          error_msg         VARCHAR(255) NULL,

          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

          UNIQUE KEY uk_symbol_kind (symbol, kind),
          KEY ix_status (status),
          KEY ix_kind (kind)
        );
    """
}


PRICE_SCHEMAS = {
    "price_history": """
        CREATE TABLE IF NOT EXISTS nyse_price_history (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,

            symbol VARCHAR(20) NOT NULL,
            timeframe ENUM('1d','1wk','1mo') NOT NULL,
            `date` DATE NOT NULL,

            open DOUBLE NULL,
            high DOUBLE NULL,
            low  DOUBLE NULL,
            close DOUBLE NULL,
            adj_close DOUBLE NULL,
            volume BIGINT NULL,

            dividends DOUBLE NULL,
            stock_splits DOUBLE NULL,

            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ON UPDATE CURRENT_TIMESTAMP,

            UNIQUE KEY uk_symbol_timeframe_date (symbol, timeframe, `date`),
            KEY ix_symbol (symbol),
            KEY ix_date (`date`)
        );
    """
}

PIT_UNIVERSE_SCHEMAS = {
    "equity_universe_snapshot": """
        CREATE TABLE IF NOT EXISTS equity_universe_snapshot (
          id BIGINT AUTO_INCREMENT PRIMARY KEY,

          universe_code VARCHAR(64) NOT NULL,
          as_of_date DATE NOT NULL,
          frequency ENUM('monthly','weekly','daily','adhoc') NOT NULL DEFAULT 'monthly',
          target_size INT NOT NULL,
          method_version VARCHAR(64) NOT NULL,
          source_basis VARCHAR(255) NOT NULL,

          candidate_count INT NOT NULL DEFAULT 0,
          eligible_count INT NOT NULL DEFAULT 0,
          member_count INT NOT NULL DEFAULT 0,
          excluded_count INT NOT NULL DEFAULT 0,
          max_rank INT NULL,
          status ENUM('ok','partial','empty','error') NOT NULL DEFAULT 'ok',
          warning_json JSON NULL,

          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

          UNIQUE KEY uk_universe_asof_method (universe_code, as_of_date, method_version),
          KEY ix_universe_asof (universe_code, as_of_date),
          KEY ix_asof (as_of_date)
        );
    """,
    "equity_universe_member": """
        CREATE TABLE IF NOT EXISTS equity_universe_member (
          id BIGINT AUTO_INCREMENT PRIMARY KEY,

          universe_code VARCHAR(64) NOT NULL,
          as_of_date DATE NOT NULL,
          symbol VARCHAR(20) NOT NULL,
          rank_no INT NULL,
          eligible TINYINT(1) NOT NULL DEFAULT 0,
          included TINYINT(1) NOT NULL DEFAULT 0,
          excluded_reason VARCHAR(128) NULL,

          price_date DATE NULL,
          close DOUBLE NULL,
          shares_outstanding BIGINT NULL,
          shares_source VARCHAR(128) NULL,
          approx_market_cap DOUBLE NULL,
          avg_dollar_volume_20d DOUBLE NULL,

          listing_status VARCHAR(32) NULL,
          lifecycle_source VARCHAR(64) NULL,
          method_version VARCHAR(64) NOT NULL,
          evidence_json JSON NULL,

          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

          UNIQUE KEY uk_universe_asof_symbol_method (universe_code, as_of_date, symbol, method_version),
          KEY ix_universe_rank (universe_code, as_of_date, included, rank_no),
          KEY ix_symbol_asof (symbol, as_of_date)
        );
    """,
}


MARKET_INTELLIGENCE_SCHEMAS = {
    "market_universe_member": """
        CREATE TABLE IF NOT EXISTS market_universe_member (
          id BIGINT AUTO_INCREMENT PRIMARY KEY,

          universe_code VARCHAR(32) NOT NULL,
          symbol VARCHAR(20) NOT NULL,
          source_symbol VARCHAR(32) NULL,
          name VARCHAR(255) NULL,
          sector VARCHAR(100) NULL,
          industry VARCHAR(150) NULL,

          source VARCHAR(64) NOT NULL,
          source_url VARCHAR(1024) NULL,
          as_of_date DATE NULL,
          active TINYINT(1) NOT NULL DEFAULT 1,
          collected_at TIMESTAMP NULL,
          error_msg TEXT NULL,

          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

          UNIQUE KEY uk_universe_symbol (universe_code, symbol),
          KEY ix_universe_active (universe_code, active),
          KEY ix_symbol (symbol)
        );
    """,
    "market_liquidity_universe_member": """
        CREATE TABLE IF NOT EXISTS market_liquidity_universe_member (
          id BIGINT AUTO_INCREMENT PRIMARY KEY,

          universe_code VARCHAR(32) NOT NULL,
          symbol VARCHAR(20) NOT NULL,
          rank_position INT NOT NULL,
          source_symbol VARCHAR(32) NULL,
          name VARCHAR(255) NULL,
          sector VARCHAR(100) NULL,
          industry VARCHAR(150) NULL,
          market_cap BIGINT NULL,

          avg_dollar_volume_20d DOUBLE NULL,
          dollar_volume_days INT NULL,
          ranking_window_start_date DATE NULL,
          ranking_end_date DATE NULL,
          ranking_source VARCHAR(128) NOT NULL,
          price_source VARCHAR(128) NULL,

          listing_source VARCHAR(64) NULL,
          listing_source_url VARCHAR(1024) NULL,
          listing_source_type VARCHAR(64) NULL,
          listing_coverage_status VARCHAR(32) NULL,
          listing_event_type VARCHAR(64) NULL,
          listing_status VARCHAR(32) NULL,
          listing_event_date DATE NULL,
          listing_collected_at TIMESTAMP NULL,

          generated_at TIMESTAMP NOT NULL,
          active TINYINT(1) NOT NULL DEFAULT 1,
          error_msg TEXT NULL,

          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

          UNIQUE KEY uk_liquidity_universe_symbol (universe_code, symbol),
          KEY ix_liquidity_universe_rank (universe_code, active, rank_position),
          KEY ix_liquidity_universe_ranking_date (universe_code, ranking_end_date),
          KEY ix_liquidity_universe_symbol (symbol)
        );
    """,
    "market_symbol_alias": """
        CREATE TABLE IF NOT EXISTS market_symbol_alias (
          id BIGINT AUTO_INCREMENT PRIMARY KEY,

          source_symbol VARCHAR(20) NOT NULL,
          alias_symbol VARCHAR(20) NOT NULL,
          alias_type VARCHAR(64) NOT NULL DEFAULT 'ticker_change',
          status ENUM('candidate','active','rejected') NOT NULL DEFAULT 'candidate',
          confidence DOUBLE NULL,
          evidence_json JSON NULL,
          detected_at TIMESTAMP NOT NULL,
          applied_at TIMESTAMP NULL,

          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

          UNIQUE KEY uk_market_symbol_alias (source_symbol, alias_symbol, alias_type),
          KEY ix_market_symbol_alias_active (source_symbol, status),
          KEY ix_market_symbol_alias_status (status, detected_at)
        );
    """,
    "market_intraday_snapshot": """
        CREATE TABLE IF NOT EXISTS market_intraday_snapshot (
          id BIGINT AUTO_INCREMENT PRIMARY KEY,

          universe_code VARCHAR(32) NOT NULL,
          symbol VARCHAR(20) NOT NULL,
          quote_symbol VARCHAR(20) NULL,
          interval_code VARCHAR(10) NOT NULL,
          snapshot_time_utc DATETIME NOT NULL,
          quote_time_utc DATETIME NULL,

          source VARCHAR(64) NOT NULL,
          source_ref VARCHAR(255) NULL,

          previous_close DOUBLE NULL,
          latest_price DOUBLE NULL,
          return_pct DOUBLE NULL,
          volume BIGINT NULL,

          provider_status ENUM('ok','missing','error') NOT NULL DEFAULT 'missing',
          error_msg TEXT NULL,

          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

          UNIQUE KEY uk_universe_symbol_interval_snapshot (universe_code, symbol, interval_code, snapshot_time_utc),
          KEY ix_universe_snapshot (universe_code, interval_code, snapshot_time_utc),
          KEY ix_symbol_snapshot (symbol, snapshot_time_utc),
          KEY ix_provider_status (provider_status)
        );
    """,
    "market_event_calendar": """
        CREATE TABLE IF NOT EXISTS market_event_calendar (
          id BIGINT AUTO_INCREMENT PRIMARY KEY,

          event_key CHAR(64) NOT NULL,
          event_date DATE NOT NULL,
          event_type VARCHAR(32) NOT NULL,
          event_family VARCHAR(32) NULL,
          event_subtype VARCHAR(64) NULL,
          event_time_label VARCHAR(64) NULL,
          event_datetime_utc TIMESTAMP NULL,
          universe_scope VARCHAR(64) NULL,
          source_authority VARCHAR(32) NULL,
          symbol VARCHAR(20) NULL,
          title VARCHAR(512) NOT NULL,

          source VARCHAR(64) NOT NULL,
          source_type VARCHAR(32) NULL,
          validation_status VARCHAR(32) NULL,
          event_status VARCHAR(32) NOT NULL DEFAULT 'active',
          superseded_by_event_key CHAR(64) NULL,
          superseded_at TIMESTAMP NULL,
          source_url VARCHAR(1024) NULL,
          confidence DOUBLE NULL,
          collected_at TIMESTAMP NULL,
          raw_payload_json JSON NULL,

          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

          UNIQUE KEY uk_market_event_key (event_key),
          KEY ix_event_date_type (event_date, event_type),
          KEY ix_event_family_date (event_family, event_date),
          KEY ix_event_universe_date (universe_scope, event_date),
          KEY ix_event_symbol_date (symbol, event_date),
          KEY ix_event_status (event_type, event_status),
          KEY ix_event_source (source)
        );
    """,
    "market_data_issue": """
        CREATE TABLE IF NOT EXISTS market_data_issue (
          id BIGINT AUTO_INCREMENT PRIMARY KEY,

          issue_key CHAR(64) NOT NULL,
          issue_type VARCHAR(64) NOT NULL,
          universe_code VARCHAR(32) NOT NULL,
          symbol VARCHAR(20) NOT NULL,
          interval_code VARCHAR(10) NULL,

          diagnosis VARCHAR(64) NOT NULL,
          latest_status VARCHAR(32) NOT NULL DEFAULT 'active',
          occurrence_count INT NOT NULL DEFAULT 1,

          first_seen_at TIMESTAMP NULL,
          last_seen_at TIMESTAMP NULL,
          last_snapshot_time_utc DATETIME NULL,

          latest_confidence DOUBLE NULL,
          latest_evidence TEXT NULL,
          latest_recommended_action TEXT NULL,
          raw_payload_json JSON NULL,

          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

          UNIQUE KEY uk_market_data_issue_key (issue_key),
          KEY ix_issue_symbol (symbol, issue_type),
          KEY ix_issue_universe_status (universe_code, latest_status),
          KEY ix_issue_last_seen (last_seen_at)
        );
    """,
}


FUTURES_MARKET_SCHEMAS = {
    "futures_instrument": """
        CREATE TABLE IF NOT EXISTS futures_instrument (
          id BIGINT AUTO_INCREMENT PRIMARY KEY,

          provider_symbol VARCHAR(32) NOT NULL,
          display_name VARCHAR(255) NOT NULL,
          futures_group VARCHAR(64) NOT NULL,
          exchange VARCHAR(64) NULL,
          contract_hint VARCHAR(255) NULL,

          source VARCHAR(64) NOT NULL DEFAULT 'yfinance',
          source_type ENUM('provider_symbol','official_mapping','manual_preset') NOT NULL DEFAULT 'manual_preset',
          active TINYINT(1) NOT NULL DEFAULT 1,
          sort_order INT NOT NULL DEFAULT 1000,
          notes TEXT NULL,

          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

          UNIQUE KEY uk_provider_symbol_source (provider_symbol, source),
          KEY ix_futures_group_active (futures_group, active),
          KEY ix_sort_order (sort_order)
        );
    """,
    "futures_market_monitor_run": """
        CREATE TABLE IF NOT EXISTS futures_market_monitor_run (
          id BIGINT AUTO_INCREMENT PRIMARY KEY,

          run_id CHAR(36) NOT NULL,
          source VARCHAR(64) NOT NULL,
          period_code VARCHAR(20) NOT NULL,
          interval_code VARCHAR(10) NOT NULL,
          cadence_mode VARCHAR(32) NOT NULL DEFAULT 'manual',

          status ENUM('success','partial_success','failed') NOT NULL DEFAULT 'failed',
          started_at TIMESTAMP NULL,
          finished_at TIMESTAMP NULL,
          duration_sec DOUBLE NULL,

          symbols_requested INT NOT NULL DEFAULT 0,
          symbols_processed INT NOT NULL DEFAULT 0,
          rows_written INT NOT NULL DEFAULT 0,
          latest_candle_time_utc DATETIME NULL,

          failed_symbols_json JSON NULL,
          diagnostics_json JSON NULL,
          message TEXT NULL,

          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

          UNIQUE KEY uk_futures_monitor_run_id (run_id),
          KEY ix_futures_monitor_finished (finished_at),
          KEY ix_futures_monitor_status (status),
          KEY ix_futures_monitor_latest_candle (latest_candle_time_utc)
        );
    """,
    "futures_ohlcv": """
        CREATE TABLE IF NOT EXISTS futures_ohlcv (
          id BIGINT AUTO_INCREMENT PRIMARY KEY,

          provider_symbol VARCHAR(32) NOT NULL,
          interval_code VARCHAR(10) NOT NULL,
          candle_time_utc DATETIME NOT NULL,

          source VARCHAR(64) NOT NULL DEFAULT 'yfinance',
          source_ref VARCHAR(255) NULL,

          open DOUBLE NULL,
          high DOUBLE NULL,
          low DOUBLE NULL,
          close DOUBLE NULL,
          adj_close DOUBLE NULL,
          volume DOUBLE NULL,

          provider_status ENUM('ok','missing','error') NOT NULL DEFAULT 'ok',
          collected_at TIMESTAMP NULL,
          error_msg TEXT NULL,

          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

          UNIQUE KEY uk_futures_symbol_interval_time_source (provider_symbol, interval_code, candle_time_utc, source),
          KEY ix_futures_symbol_time (provider_symbol, candle_time_utc),
          KEY ix_futures_interval_time (interval_code, candle_time_utc),
          KEY ix_futures_provider_status (provider_status)
        );
    """,
    "futures_macro_snapshot": """
        CREATE TABLE IF NOT EXISTS futures_macro_snapshot (
          id BIGINT AUTO_INCREMENT PRIMARY KEY,

          snapshot_key VARCHAR(64) NOT NULL,
          source_marker VARCHAR(64) NOT NULL,
          as_of_date DATE NULL,
          schema_version VARCHAR(64) NOT NULL,
          algorithm_version VARCHAR(128) NOT NULL,
          status ENUM('READY','LIMITED','ERROR') NOT NULL,
          snapshot_json LONGTEXT NOT NULL,
          materialized_at TIMESTAMP NOT NULL,

          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

          UNIQUE KEY uk_futures_macro_snapshot_key (snapshot_key),
          KEY ix_futures_macro_snapshot_marker (source_marker),
          KEY ix_futures_macro_snapshot_version (schema_version, algorithm_version)
        );
    """,
}


PROVIDER_SCHEMAS = {
    "etf_provider_source_map": """
        CREATE TABLE IF NOT EXISTS etf_provider_source_map (
          id BIGINT AUTO_INCREMENT PRIMARY KEY,

          symbol VARCHAR(20) NOT NULL,
          provider VARCHAR(64) NOT NULL,
          data_kind ENUM('operability','holdings','exposure') NOT NULL,
          parser VARCHAR(64) NOT NULL,
          source_url VARCHAR(1024) NOT NULL,
          source_ref VARCHAR(1024) NULL,

          source_status ENUM('verified','candidate','missing','failed','unsupported') NOT NULL DEFAULT 'candidate',
          fund_family VARCHAR(255) NULL,
          product_id VARCHAR(64) NULL,
          product_slug VARCHAR(255) NULL,
          discovered_from VARCHAR(128) NULL,

          metadata_json JSON NULL,
          verified_at TIMESTAMP NULL,
          last_checked_at TIMESTAMP NULL,
          error_msg TEXT NULL,

          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

          UNIQUE KEY uk_symbol_kind_provider_parser (symbol, data_kind, provider, parser),
          KEY ix_symbol_kind (symbol, data_kind),
          KEY ix_provider_kind (provider, data_kind),
          KEY ix_source_status (source_status)
        );
    """,
    "etf_operability_snapshot": """
        CREATE TABLE IF NOT EXISTS etf_operability_snapshot (
          id BIGINT AUTO_INCREMENT PRIMARY KEY,

          symbol VARCHAR(20) NOT NULL,
          as_of_date DATE NOT NULL,
          source VARCHAR(64) NOT NULL,
          source_type ENUM('official','database_bridge','computed_proxy') NOT NULL,
          source_ref VARCHAR(255) NULL,

          fund_family VARCHAR(255) NULL,
          category VARCHAR(255) NULL,

          expense_ratio DOUBLE NULL,
          turnover_ratio DOUBLE NULL,
          total_assets DOUBLE NULL,
          net_assets DOUBLE NULL,
          nav DOUBLE NULL,
          market_price DOUBLE NULL,
          premium_discount_pct DOUBLE NULL,

          bid DOUBLE NULL,
          ask DOUBLE NULL,
          bid_ask_spread_pct DOUBLE NULL,
          median_bid_ask_spread_pct DOUBLE NULL,

          avg_daily_volume DOUBLE NULL,
          avg_daily_dollar_volume DOUBLE NULL,
          lookback_days INT NULL,

          inception_date DATE NULL,
          leverage_factor DOUBLE NULL,
          is_inverse TINYINT(1) NULL,
          has_daily_objective TINYINT(1) NULL,

          coverage_status ENUM('actual','partial','bridge','proxy','missing','error') NOT NULL DEFAULT 'missing',
          missing_fields_json JSON NULL,
          collected_at TIMESTAMP NULL,
          error_msg TEXT NULL,

          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

          UNIQUE KEY uk_symbol_asof_source (symbol, as_of_date, source),
          KEY ix_symbol_asof (symbol, as_of_date),
          KEY ix_coverage_status (coverage_status)
        );
    """,
    "etf_holdings_snapshot": """
        CREATE TABLE IF NOT EXISTS etf_holdings_snapshot (
          id BIGINT AUTO_INCREMENT PRIMARY KEY,

          fund_symbol VARCHAR(20) NOT NULL,
          as_of_date DATE NOT NULL,
          source VARCHAR(64) NOT NULL,
          source_type ENUM('official','database_bridge','computed_proxy') NOT NULL,
          source_ref VARCHAR(255) NULL,

          holding_id VARCHAR(255) NOT NULL,
          holding_symbol VARCHAR(64) NULL,
          holding_name VARCHAR(512) NOT NULL,
          holding_type VARCHAR(128) NULL,

          cusip VARCHAR(32) NULL,
          isin VARCHAR(32) NULL,
          lei VARCHAR(32) NULL,
          issuer_cik VARCHAR(16) NULL,
          filing_date DATE NULL,
          accession_no VARCHAR(32) NULL,
          holding_snapshot_quality ENUM('annual_anchor','quarterly_anchor','current_issuer_snapshot') NULL,

          weight_pct DOUBLE NULL,
          shares DOUBLE NULL,
          market_value DOUBLE NULL,

          sector VARCHAR(255) NULL,
          asset_class VARCHAR(128) NULL,
          country VARCHAR(128) NULL,
          currency VARCHAR(16) NULL,

          coverage_status ENUM('actual','partial','bridge','proxy','missing','error') NOT NULL DEFAULT 'actual',
          missing_fields_json JSON NULL,
          collected_at TIMESTAMP NULL,
          error_msg TEXT NULL,

          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

          UNIQUE KEY uk_fund_asof_source_holding (fund_symbol, as_of_date, source, holding_id),
          KEY ix_fund_asof (fund_symbol, as_of_date),
          KEY ix_holding_symbol (holding_symbol),
          KEY ix_coverage_status (coverage_status)
        );
    """,
    "etf_exposure_snapshot": """
        CREATE TABLE IF NOT EXISTS etf_exposure_snapshot (
          id BIGINT AUTO_INCREMENT PRIMARY KEY,

          fund_symbol VARCHAR(20) NOT NULL,
          as_of_date DATE NOT NULL,
          source VARCHAR(64) NOT NULL,
          source_type ENUM('official','database_bridge','computed_proxy') NOT NULL,
          source_ref VARCHAR(255) NULL,
          derived_from VARCHAR(128) NOT NULL,

          exposure_type VARCHAR(64) NOT NULL,
          exposure_name VARCHAR(255) NOT NULL,
          weight_pct DOUBLE NULL,

          coverage_status ENUM('actual','partial','bridge','proxy','missing','error') NOT NULL DEFAULT 'actual',
          missing_fields_json JSON NULL,
          collected_at TIMESTAMP NULL,
          error_msg TEXT NULL,

          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

          UNIQUE KEY uk_fund_asof_source_exposure (fund_symbol, as_of_date, source, exposure_type, exposure_name),
          KEY ix_fund_asof (fund_symbol, as_of_date),
          KEY ix_exposure_type (exposure_type),
          KEY ix_coverage_status (coverage_status)
        );
    """,
    "macro_series_observation": """
        CREATE TABLE IF NOT EXISTS macro_series_observation (
          id BIGINT AUTO_INCREMENT PRIMARY KEY,

          series_id VARCHAR(64) NOT NULL,
          observation_date DATE NOT NULL,
          source VARCHAR(64) NOT NULL,
          source_type ENUM('official','database_bridge','computed_proxy') NOT NULL DEFAULT 'official',
          source_mode VARCHAR(32) NULL,
          source_ref VARCHAR(255) NULL,

          series_name VARCHAR(255) NULL,
          category VARCHAR(64) NOT NULL,
          frequency VARCHAR(32) NULL,
          units VARCHAR(64) NULL,
          value DOUBLE NULL,
          release_lag_days INT NULL,

          coverage_status ENUM('actual','partial','bridge','proxy','missing','error') NOT NULL DEFAULT 'actual',
          missing_fields_json JSON NULL,
          collected_at TIMESTAMP NULL,
          error_msg TEXT NULL,

          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

          UNIQUE KEY uk_series_date_source (series_id, observation_date, source),
          KEY ix_series_date (series_id, observation_date),
          KEY ix_category_date (category, observation_date),
          KEY ix_coverage_status (coverage_status)
        );
    """,
    "market_sentiment_collection_batch": """
        CREATE TABLE IF NOT EXISTS market_sentiment_collection_batch (
          batch_id CHAR(36) PRIMARY KEY,
          collection_id CHAR(36) NOT NULL,
          source VARCHAR(64) NOT NULL,
          source_ref VARCHAR(1024) NULL,
          schema_version VARCHAR(64) NOT NULL,
          status ENUM('success','partial','missing','error') NOT NULL,
          requested_at DATETIME(6) NOT NULL,
          observed_at DATETIME(6) NULL,
          completed_at DATETIME(6) NOT NULL,
          observation_start DATE NULL,
          observation_end DATE NULL,
          row_count INT NOT NULL DEFAULT 0,
          coverage_json JSON NULL,
          error_msg TEXT NULL,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          KEY ix_sentiment_batch_collection (collection_id),
          KEY ix_sentiment_batch_source_observed (source, observed_at),
          KEY ix_sentiment_batch_status_completed (status, completed_at)
        );
    """,
    "market_sentiment_observation_snapshot": """
        CREATE TABLE IF NOT EXISTS market_sentiment_observation_snapshot (
          id BIGINT AUTO_INCREMENT PRIMARY KEY,
          batch_id CHAR(36) NOT NULL,
          collection_id CHAR(36) NOT NULL,
          series_id VARCHAR(64) NOT NULL,
          observation_date DATE NOT NULL,
          source VARCHAR(64) NOT NULL,
          source_type ENUM('official','database_bridge','computed_proxy') NOT NULL DEFAULT 'official',
          source_mode VARCHAR(32) NULL,
          source_ref VARCHAR(1024) NULL,
          series_name VARCHAR(255) NULL,
          category VARCHAR(64) NOT NULL,
          frequency VARCHAR(32) NULL,
          units VARCHAR(64) NULL,
          value DOUBLE NULL,
          release_lag_days INT NULL,
          coverage_status ENUM('actual','partial','bridge','proxy','missing','error') NOT NULL DEFAULT 'actual',
          missing_fields_json JSON NULL,
          observed_at DATETIME(6) NOT NULL,
          error_msg TEXT NULL,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          UNIQUE KEY uk_sentiment_snapshot_batch_series_date_source
            (batch_id, series_id, observation_date, source),
          KEY ix_sentiment_snapshot_batch (batch_id),
          KEY ix_sentiment_snapshot_as_known (series_id, source, observed_at, observation_date),
          KEY ix_sentiment_snapshot_collection (collection_id)
        );
    """,
    "macro_series_vintage_observation": """
        CREATE TABLE IF NOT EXISTS macro_series_vintage_observation (
          id BIGINT AUTO_INCREMENT PRIMARY KEY,

          series_id VARCHAR(64) NOT NULL,
          observation_date DATE NOT NULL,
          realtime_start DATE NOT NULL,
          realtime_end DATE NOT NULL,
          source VARCHAR(64) NOT NULL DEFAULT 'fred',
          source_type ENUM('official','database_bridge','computed_proxy') NOT NULL DEFAULT 'official',
          source_mode VARCHAR(64) NOT NULL DEFAULT 'fred_output_type_1_realtime_intervals',
          source_ref VARCHAR(1024) NULL,

          series_name VARCHAR(255) NULL,
          factor_group VARCHAR(64) NOT NULL,
          frequency VARCHAR(32) NULL,
          units VARCHAR(64) NULL,
          value DECIMAL(24,10) NULL,
          release_lag_days INT NULL,

          coverage_status ENUM('actual','partial','missing','error') NOT NULL DEFAULT 'actual',
          missing_fields_json TEXT NULL,
          collected_at TIMESTAMP NULL,
          error_msg TEXT NULL,

          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

          UNIQUE KEY uk_series_observation_realtime_source (series_id, observation_date, realtime_start, source),
          KEY ix_series_realtime_observation (series_id, realtime_start, observation_date),
          KEY ix_factor_observation (factor_group, observation_date),
          KEY ix_vintage_coverage_status (coverage_status)
        );
    """
}


ECONOMIC_CYCLE_SCHEMAS = {
    "economic_cycle_model_artifact": """
        CREATE TABLE IF NOT EXISTS economic_cycle_model_artifact (
          id BIGINT AUTO_INCREMENT PRIMARY KEY,

          model_version VARCHAR(128) NOT NULL,
          trained_through DATE NOT NULL,
          feature_schema_version VARCHAR(128) NOT NULL,
          parameters_json LONGTEXT NOT NULL,
          validation_metrics_json LONGTEXT NOT NULL,
          publication_status ENUM('READY','LIMITED','ERROR') NOT NULL,
          publication_status_json LONGTEXT NOT NULL,

          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

          UNIQUE KEY uk_cycle_model_trained (model_version, trained_through),
          KEY ix_cycle_model_status_trained (publication_status, trained_through)
        );
    """,
    "economic_cycle_snapshot": """
        CREATE TABLE IF NOT EXISTS economic_cycle_snapshot (
          id BIGINT AUTO_INCREMENT PRIMARY KEY,

          as_of_date DATE NOT NULL,
          model_version VARCHAR(128) NOT NULL,
          run_kind ENUM('historical_replay','current') NOT NULL,
          training_cutoff_date DATE NOT NULL,
          data_cutoff_date DATE NOT NULL,
          status ENUM('READY','LIMITED','ERROR') NOT NULL,
          current_phase ENUM('recovery','expansion','slowdown','recession') NULL,
          expected_transition VARCHAR(128) NULL,
          nber_recession TINYINT(1) NOT NULL DEFAULT 0,

          probabilities_json LONGTEXT NOT NULL,
          forecast_path_json LONGTEXT NOT NULL,
          factor_contributions_json LONGTEXT NOT NULL,
          top_evidence_json LONGTEXT NOT NULL,
          warnings_json LONGTEXT NOT NULL,

          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

          UNIQUE KEY uk_cycle_snapshot (as_of_date, model_version, run_kind),
          KEY ix_cycle_snapshot_date_status (as_of_date, status),
          KEY ix_cycle_snapshot_kind_date (run_kind, as_of_date)
        );
    """,
}


INSTITUTIONAL_13F_SCHEMAS = {
    "institutional_13f_manager": """
        CREATE TABLE IF NOT EXISTS institutional_13f_manager (
          cik VARCHAR(10) PRIMARY KEY,
          manager_name VARCHAR(255) NOT NULL,

          latest_accession_number VARCHAR(25) NULL,
          latest_report_period DATE NULL,
          latest_filing_date DATE NULL,
          filing_count INT NOT NULL DEFAULT 0,

          source VARCHAR(64) NOT NULL DEFAULT 'sec_form_13f_dataset',
          source_ref VARCHAR(1024) NULL,
          last_collected_at TIMESTAMP NULL,

          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

          KEY ix_manager_name (manager_name),
          KEY ix_latest_accession_number (latest_accession_number),
          KEY ix_latest_report_period (latest_report_period),
          KEY ix_latest_filing_date (latest_filing_date)
        );
    """,
    "institutional_13f_filing": """
        CREATE TABLE IF NOT EXISTS institutional_13f_filing (
          accession_number VARCHAR(25) PRIMARY KEY,
          cik VARCHAR(10) NOT NULL,
          manager_name VARCHAR(255) NOT NULL,

          submission_type VARCHAR(10) NOT NULL,
          filing_date DATE NOT NULL,
          period_of_report DATE NOT NULL,
          report_calendar_or_quarter DATE NULL,

          is_amendment TINYINT(1) NOT NULL DEFAULT 0,
          amendment_no INT NULL,
          amendment_type VARCHAR(64) NULL,
          report_type VARCHAR(64) NULL,
          form13f_file_number VARCHAR(32) NULL,

          table_entry_total INT NULL,
          table_value_total DECIMAL(24,4) NULL,
          is_confidential_omitted TINYINT(1) NULL,

          source_dataset VARCHAR(128) NOT NULL,
          source_ref VARCHAR(1024) NULL,
          collected_at TIMESTAMP NULL,

          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

          KEY ix_cik_period (cik, period_of_report),
          KEY ix_manager_name (manager_name),
          KEY ix_period_filing (period_of_report, filing_date),
          KEY ix_source_dataset (source_dataset)
        );
    """,
    "institutional_13f_holding": """
        CREATE TABLE IF NOT EXISTS institutional_13f_holding (
          id BIGINT AUTO_INCREMENT PRIMARY KEY,

          accession_number VARCHAR(25) NOT NULL,
          infotable_sk BIGINT NOT NULL,
          cik VARCHAR(10) NOT NULL,
          manager_name VARCHAR(255) NOT NULL,
          report_period DATE NOT NULL,
          filing_date DATE NOT NULL,

          issuer_name VARCHAR(255) NOT NULL,
          title_of_class VARCHAR(150) NULL,
          cusip CHAR(9) NOT NULL,
          figi VARCHAR(16) NULL,

          reported_value DECIMAL(24,4) NULL,
          shares_or_principal_amount DECIMAL(24,4) NULL,
          amount_type VARCHAR(10) NULL,
          put_call VARCHAR(10) NULL,
          investment_discretion VARCHAR(32) NULL,
          other_manager VARCHAR(128) NULL,
          voting_auth_sole DECIMAL(24,4) NULL,
          voting_auth_shared DECIMAL(24,4) NULL,
          voting_auth_none DECIMAL(24,4) NULL,

          holding_symbol VARCHAR(20) NULL,
          symbol_source VARCHAR(64) NULL,
          sector VARCHAR(100) NULL,
          industry VARCHAR(150) NULL,

          source_dataset VARCHAR(128) NOT NULL,
          source_ref VARCHAR(1024) NULL,
          collected_at TIMESTAMP NULL,

          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

          UNIQUE KEY uk_accession_info_table (accession_number, infotable_sk),
          KEY ix_cik_period (cik, report_period),
          KEY ix_report_period_cusip_cik (report_period, cusip, cik),
          KEY ix_cusip (cusip),
          KEY ix_holding_symbol (holding_symbol),
          KEY ix_sector (sector),
          KEY ix_source_dataset (source_dataset)
        );
    """,
    "institutional_13f_cusip_symbol_map": """
        CREATE TABLE IF NOT EXISTS institutional_13f_cusip_symbol_map (
          id BIGINT AUTO_INCREMENT PRIMARY KEY,

          cusip CHAR(9) NOT NULL,
          symbol VARCHAR(20) NOT NULL,
          issuer_name VARCHAR(255) NULL,
          figi VARCHAR(16) NULL,
          sector VARCHAR(100) NULL,
          industry VARCHAR(150) NULL,

          source VARCHAR(64) NOT NULL,
          confidence DOUBLE NULL,
          source_ref VARCHAR(1024) NULL,
          verified_at TIMESTAMP NULL,

          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

          UNIQUE KEY uk_cusip_symbol_source (cusip, symbol, source),
          KEY ix_cusip (cusip),
          KEY ix_symbol (symbol),
          KEY ix_source (source)
        );
    """,
    "institutional_13f_identifier_resolution": """
        CREATE TABLE IF NOT EXISTS institutional_13f_identifier_resolution (
          id BIGINT AUTO_INCREMENT PRIMARY KEY,

          identifier_value CHAR(9) NOT NULL,
          identifier_type VARCHAR(16) NOT NULL,
          source VARCHAR(64) NOT NULL,
          resolution_status VARCHAR(16) NOT NULL,
          symbol VARCHAR(20) NULL,
          provider_name VARCHAR(255) NULL,
          figi VARCHAR(16) NULL,
          candidate_count INT NOT NULL DEFAULT 0,
          candidates_json JSON NULL,
          source_ref VARCHAR(1024) NULL,
          warning_text TEXT NULL,
          error_text TEXT NULL,
          last_attempt_status VARCHAR(16) NOT NULL,
          attempted_at TIMESTAMP NULL,
          resolved_at TIMESTAMP NULL,

          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

          UNIQUE KEY uk_identifier_source (identifier_value, source),
          KEY ix_resolution_status (resolution_status),
          KEY ix_resolution_symbol (symbol),
          KEY ix_last_attempt_status (last_attempt_status)
        );
    """,
    "institutional_13f_manager_watchlist": """
        CREATE TABLE IF NOT EXISTS institutional_13f_manager_watchlist (
          cik VARCHAR(10) PRIMARY KEY,
          display_name VARCHAR(255) NOT NULL,
          watchlist_label VARCHAR(100) NULL,
          alias VARCHAR(255) NULL,
          priority INT NOT NULL DEFAULT 100,
          tags_json JSON NULL,
          external_links_json JSON NULL,
          source VARCHAR(64) NOT NULL DEFAULT 'seed_config',
          active TINYINT(1) NOT NULL DEFAULT 1,
          notes TEXT NULL,

          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

          KEY ix_active_priority (active, priority),
          KEY ix_display_name (display_name)
        );
    """,
    "institutional_13f_refresh_status": """
        CREATE TABLE IF NOT EXISTS institutional_13f_refresh_status (
          source_key VARCHAR(64) PRIMARY KEY,
          source_dataset VARCHAR(128) NULL,
          source_ref VARCHAR(1024) NULL,
          status VARCHAR(32) NOT NULL DEFAULT 'unknown',

          last_collected_at TIMESTAMP NULL,
          latest_report_period DATE NULL,
          latest_filing_date DATE NULL,
          managers_written INT NOT NULL DEFAULT 0,
          filings_written INT NOT NULL DEFAULT 0,
          holdings_written INT NOT NULL DEFAULT 0,
          rows_written INT NOT NULL DEFAULT 0,

          is_stale TINYINT(1) NOT NULL DEFAULT 1,
          stale_reason TEXT NULL,
          error_message TEXT NULL,
          source_limitations_json JSON NULL,

          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

          KEY ix_status_collected (status, last_collected_at),
          KEY ix_latest_report_period (latest_report_period)
        );
    """,
}


PORTFOLIO_MONITORING_SCHEMAS = {
    "monitoring_portfolio_group": """
        CREATE TABLE IF NOT EXISTS monitoring_portfolio_group (
          portfolio_group_id VARCHAR(64) PRIMARY KEY,
          name VARCHAR(255) NOT NULL,
          is_default TINYINT(1) NOT NULL DEFAULT 0,
          status ENUM('active','archived') NOT NULL DEFAULT 'active',
          version BIGINT NOT NULL DEFAULT 1,
          metadata_json JSON NULL,

          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          deleted_at TIMESTAMP NULL,

          KEY ix_monitoring_group_status (status, deleted_at),
          KEY ix_monitoring_group_default (is_default, status)
        );
    """,
    "monitoring_portfolio_item": """
        CREATE TABLE IF NOT EXISTS monitoring_portfolio_item (
          monitoring_item_id VARCHAR(64) PRIMARY KEY,
          portfolio_group_id VARCHAR(64) NOT NULL,
          source_type ENUM('direct_security','selected_strategy') NOT NULL,
          source_ref VARCHAR(128) NOT NULL,
          instrument_kind ENUM('stock','etf','strategy') NOT NULL,

          requested_start_date DATE NOT NULL,
          effective_start_date DATE NOT NULL,
          funding_mode ENUM('fixed_notional','fixed_shares') NOT NULL,
          input_notional DECIMAL(24,8) NULL,
          input_shares BIGINT NULL,
          entry_close DECIMAL(24,8) NOT NULL,
          initial_capital DECIMAL(24,8) NOT NULL,

          tracking_end_requested_date DATE NULL,
          tracking_end_effective_date DATE NULL,
          exit_value DECIMAL(24,8) NULL,
          status ENUM('active','ended','data_review') NOT NULL DEFAULT 'active',
          metadata_json JSON NULL,

          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

          KEY ix_monitoring_item_group_status (portfolio_group_id, status),
          KEY ix_monitoring_item_source (source_type, source_ref),
          KEY ix_monitoring_item_effective_start (effective_start_date),
          KEY ix_monitoring_item_effective_end (tracking_end_effective_date)
        );
    """,
    "monitoring_portfolio_command": """
        CREATE TABLE IF NOT EXISTS monitoring_portfolio_command (
          command_id VARCHAR(64) PRIMARY KEY,
          command_type VARCHAR(32) NOT NULL,
          target_id VARCHAR(128) NULL,
          request_fingerprint CHAR(64) NOT NULL,
          status ENUM('pending','succeeded','failed') NOT NULL DEFAULT 'pending',
          result_ref VARCHAR(128) NULL,
          result_json JSON NULL,
          error_message TEXT NULL,

          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

          KEY ix_monitoring_command_target (target_id, created_at),
          KEY ix_monitoring_command_status (status, created_at)
        );
    """,
    "monitoring_diagnosis_snapshot": """
        CREATE TABLE IF NOT EXISTS monitoring_diagnosis_snapshot (
          diagnosis_snapshot_id BIGINT AUTO_INCREMENT PRIMARY KEY,
          portfolio_group_id VARCHAR(64) NOT NULL,
          as_of_date DATE NOT NULL,
          config_fingerprint CHAR(64) NOT NULL,
          policy_version VARCHAR(128) NOT NULL,
          macro_version VARCHAR(128) NOT NULL,
          publication_time DATETIME NOT NULL,
          source_dates_json JSON NOT NULL,
          observations_json JSON NOT NULL,
          outcome_21 DOUBLE NULL,
          outcome_63 DOUBLE NULL,
          outcome_status VARCHAR(32) NOT NULL DEFAULT 'pending',
          outcome_measured_at DATE NULL,

          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

          UNIQUE KEY uk_monitoring_diagnosis_identity
            (portfolio_group_id, as_of_date, config_fingerprint, policy_version),
          KEY ix_monitoring_diagnosis_group_date (portfolio_group_id, as_of_date),
          KEY ix_monitoring_diagnosis_publication (publication_time)
        );
    """,
    "monitoring_risk_calibration_artifact": """
        CREATE TABLE IF NOT EXISTS monitoring_risk_calibration_artifact (
          calibration_artifact_id CHAR(64) PRIMARY KEY,
          algorithm_version VARCHAR(128) NOT NULL,
          data_fingerprint CHAR(64) NOT NULL,
          config_fingerprint CHAR(64) NOT NULL,
          policy_version VARCHAR(128) NOT NULL,
          publication_status ENUM('SUPPRESSED','LIMITED','READY') NOT NULL,
          train_end_date DATE NULL,
          validation_start_date DATE NULL,
          validation_end_date DATE NULL,
          horizon_sessions INT NOT NULL,
          event_definition VARCHAR(255) NOT NULL,
          sample_size INT NOT NULL,
          positive_count INT NOT NULL,
          brier_score DOUBLE NULL,
          baseline_brier DOUBLE NULL,
          max_reliability_error DOUBLE NULL,
          probability DOUBLE NULL,
          artifact_json JSON NOT NULL,

          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

          UNIQUE KEY uk_monitoring_calibration_fingerprint
            (algorithm_version, data_fingerprint, config_fingerprint, policy_version, horizon_sessions),
          KEY ix_monitoring_calibration_status (publication_status, created_at)
        );
    """,
}


VALUATION_SCHEMAS = {
    "nasdaq100_monthly_valuation": """
        CREATE TABLE IF NOT EXISTS nasdaq100_monthly_valuation (
          id BIGINT AUTO_INCREMENT PRIMARY KEY,

          observation_month DATE NOT NULL,
          proxy_symbol VARCHAR(20) NOT NULL DEFAULT 'QQQ',
          qqq_price DOUBLE NULL,
          reconstructed_ttm_eps DOUBLE NULL,
          trailing_pe DOUBLE NULL,
          earnings_yield DOUBLE NULL,

          coverage_weight_pct DOUBLE NOT NULL DEFAULT 0,
          unmapped_weight_pct DOUBLE NOT NULL DEFAULT 100,
          holding_snapshot_date DATE NULL,
          holding_snapshot_quality ENUM('annual_anchor','quarterly_anchor','current_issuer_snapshot') NULL,
          earnings_available_through DATE NULL,
          price_basis_date DATE NULL,

          data_quality ENUM('reconstructed_actual','partial','blocked') NOT NULL,
          source VARCHAR(64) NOT NULL,
          source_ref VARCHAR(1024) NULL,
          collected_at TIMESTAMP NULL,
          error_msg TEXT NULL,

          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

          UNIQUE KEY uk_nasdaq100_month_proxy_source (observation_month, proxy_symbol, source),
          KEY ix_nasdaq100_month (observation_month),
          KEY ix_nasdaq100_quality (data_quality)
        );
    """,
    "sp500_monthly_valuation": """
        CREATE TABLE IF NOT EXISTS sp500_monthly_valuation (
          id BIGINT AUTO_INCREMENT PRIMARY KEY,

          observation_month DATE NOT NULL,
          spx_level DOUBLE NULL,
          trailing_eps DOUBLE NULL,
          trailing_pe DOUBLE NULL,
          cape DOUBLE NULL,

          data_quality ENUM('actual','interpolated','estimate','missing','error') NOT NULL,
          source VARCHAR(64) NOT NULL,
          source_ref VARCHAR(1024) NULL,
          source_version VARCHAR(128) NULL,
          collected_at TIMESTAMP NULL,
          error_msg TEXT NULL,

          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

          UNIQUE KEY uk_sp500_month_source (observation_month, source),
          KEY ix_sp500_month (observation_month)
        );
    """,
    "sp500_index_earnings": """
        CREATE TABLE IF NOT EXISTS sp500_index_earnings (
          id BIGINT AUTO_INCREMENT PRIMARY KEY,

          period_end DATE NOT NULL,
          period_type ENUM('quarterly','annual','ttm') NOT NULL,
          earnings_basis ENUM('as_reported','operating') NOT NULL,
          value_status ENUM('actual','estimate','mixed') NOT NULL,
          eps DOUBLE NOT NULL,

          source VARCHAR(64) NOT NULL,
          source_ref VARCHAR(1024) NULL,
          source_release_date DATE NOT NULL,
          collected_at TIMESTAMP NULL,
          error_msg TEXT NULL,

          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

          UNIQUE KEY uk_sp500_eps_period_basis_status_source
            (period_end, period_type, earnings_basis, value_status, source, source_release_date),
          KEY ix_sp500_eps_period (period_end, period_type)
        );
    """,
    "fomc_sep_projection": """
        CREATE TABLE IF NOT EXISTS fomc_sep_projection (
          id BIGINT AUTO_INCREMENT PRIMARY KEY,

          release_date DATE NOT NULL,
          target_year SMALLINT NOT NULL,
          variable_name ENUM('real_gdp','pce_inflation') NOT NULL,
          statistic_name ENUM(
            'median',
            'central_tendency_lower',
            'central_tendency_upper',
            'range_lower',
            'range_upper'
          ) NOT NULL,
          value_pct DOUBLE NOT NULL,

          source VARCHAR(64) NOT NULL DEFAULT 'federal_reserve_sep',
          source_ref VARCHAR(1024) NOT NULL,
          collected_at TIMESTAMP NULL,
          error_msg TEXT NULL,

          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

          UNIQUE KEY uk_sep_release_year_variable_stat
            (release_date, target_year, variable_name, statistic_name),
          KEY ix_sep_latest (release_date, target_year)
        );
    """,
}


FUNDAMENTAL_SCHEMAS = {
    "fundamentals": """
        CREATE TABLE IF NOT EXISTS nyse_fundamentals (
          id BIGINT AUTO_INCREMENT PRIMARY KEY,

          symbol VARCHAR(20) NOT NULL,
          freq   ENUM('annual','quarterly') NOT NULL,
          period_end DATE NOT NULL,

          currency VARCHAR(10) NULL,

          total_revenue DOUBLE NULL,
          gross_profit DOUBLE NULL,
          operating_income DOUBLE NULL,
          ebit DOUBLE NULL,
          pretax_income DOUBLE NULL,
          interest_expense DOUBLE NULL,
          net_income DOUBLE NULL,

          total_assets DOUBLE NULL,
          current_assets DOUBLE NULL,
          inventory DOUBLE NULL,
          total_liabilities DOUBLE NULL,
          current_liabilities DOUBLE NULL,
          short_term_debt DOUBLE NULL,
          long_term_debt DOUBLE NULL,
          total_debt DOUBLE NULL,
          shareholders_equity DOUBLE NULL,
          net_assets DOUBLE NULL,

          operating_cash_flow DOUBLE NULL,
          free_cash_flow DOUBLE NULL,
          capital_expenditure DOUBLE NULL,
          cash_and_equivalents DOUBLE NULL,

          dividends_paid DOUBLE NULL,
          shares_outstanding BIGINT NULL,

          source_mode VARCHAR(32) NOT NULL DEFAULT 'provider_summary',
          timing_basis VARCHAR(32) NOT NULL DEFAULT 'period_end',
          gross_profit_source VARCHAR(32) NULL,
          operating_income_source VARCHAR(32) NULL,
          ebit_source VARCHAR(32) NULL,
          free_cash_flow_source VARCHAR(32) NULL,
          shares_outstanding_source VARCHAR(32) NULL,
          total_debt_source VARCHAR(32) NULL,
          shareholders_equity_source VARCHAR(32) NULL,

          source VARCHAR(20) NOT NULL DEFAULT 'yfinance',
          last_collected_at TIMESTAMP NULL,
          error_msg TEXT NULL,

          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

          UNIQUE KEY uk_symbol_freq_period (symbol, freq, period_end),
          KEY ix_symbol (symbol),
          KEY ix_period_end (period_end)
        );
    """,

    "fundamentals_statement": """
        CREATE TABLE IF NOT EXISTS nyse_fundamentals_statement (
          id BIGINT AUTO_INCREMENT PRIMARY KEY,

          symbol VARCHAR(20) NOT NULL,
          freq   ENUM('annual','quarterly') NOT NULL,
          period_end DATE NOT NULL,

          currency VARCHAR(10) NULL,

          total_revenue DOUBLE NULL,
          gross_profit DOUBLE NULL,
          operating_income DOUBLE NULL,
          ebit DOUBLE NULL,
          pretax_income DOUBLE NULL,
          interest_expense DOUBLE NULL,
          net_income DOUBLE NULL,

          total_assets DOUBLE NULL,
          current_assets DOUBLE NULL,
          inventory DOUBLE NULL,
          total_liabilities DOUBLE NULL,
          current_liabilities DOUBLE NULL,
          short_term_debt DOUBLE NULL,
          long_term_debt DOUBLE NULL,
          total_debt DOUBLE NULL,
          shareholders_equity DOUBLE NULL,
          net_assets DOUBLE NULL,

          operating_cash_flow DOUBLE NULL,
          free_cash_flow DOUBLE NULL,
          capital_expenditure DOUBLE NULL,
          cash_and_equivalents DOUBLE NULL,

          dividends_paid DOUBLE NULL,
          shares_outstanding BIGINT NULL,

          latest_available_at DATETIME NULL,
          latest_accession_no VARCHAR(32) NULL,
          latest_form_type VARCHAR(20) NULL,

          source_mode VARCHAR(32) NOT NULL DEFAULT 'statement_ledger_shadow',
          timing_basis VARCHAR(32) NOT NULL DEFAULT 'latest_available_for_period_end',
          gross_profit_source VARCHAR(64) NULL,
          operating_income_source VARCHAR(64) NULL,
          ebit_source VARCHAR(64) NULL,
          free_cash_flow_source VARCHAR(64) NULL,
          shares_outstanding_source VARCHAR(64) NULL,
          total_debt_source VARCHAR(128) NULL,
          shareholders_equity_source VARCHAR(64) NULL,

          source VARCHAR(20) NOT NULL DEFAULT 'statement_ledger',
          last_collected_at TIMESTAMP NULL,
          error_msg TEXT NULL,

          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

          UNIQUE KEY uk_symbol_freq_period (symbol, freq, period_end),
          KEY ix_symbol (symbol),
          KEY ix_period_end (period_end),
          KEY ix_symbol_available_at (symbol, latest_available_at)
        );
    """,

    "financial_statement_filings": """
        CREATE TABLE IF NOT EXISTS nyse_financial_statement_filings (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,

        symbol VARCHAR(20) NOT NULL,
        accession_no VARCHAR(32) NOT NULL,
        form_type VARCHAR(20) NULL,
        filing_date DATE NULL,
        accepted_at DATETIME NULL,
        available_at DATETIME NULL,
        report_date DATE NULL,

        file_number VARCHAR(40) NULL,
        primary_document VARCHAR(255) NULL,
        primary_doc_description VARCHAR(255) NULL,
        is_xbrl TINYINT(1) NULL,
        is_inline_xbrl TINYINT(1) NULL,
        size BIGINT NULL,

        source VARCHAR(20) NOT NULL DEFAULT 'edgar',
        last_collected_at TIMESTAMP NULL,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

        UNIQUE KEY uk_symbol_accession (symbol, accession_no),
        KEY ix_symbol_filing_date (symbol, filing_date),
        KEY ix_symbol_available_at (symbol, available_at),
        KEY ix_form_type (form_type)
        );
    """,

    "financial_statement_values": """
        CREATE TABLE IF NOT EXISTS nyse_financial_statement_values (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,

        symbol VARCHAR(20) NOT NULL,
        freq   ENUM('annual','quarterly') NOT NULL,
        period_start DATE NULL,
        period_end DATE NOT NULL,
        period_label VARCHAR(20) NULL,
        period_type ENUM('Q','FY','DATE') NULL,
        source_period_type VARCHAR(20) NULL,
        fiscal_year SMALLINT NULL,
        fiscal_period VARCHAR(10) NULL,
        fiscal_quarter TINYINT NULL,

        statement_type VARCHAR(50) NOT NULL,
        concept VARCHAR(255) NOT NULL,
        taxonomy VARCHAR(50) NULL,
        label VARCHAR(255) NOT NULL,
        value DOUBLE NULL,
        unit VARCHAR(32) NOT NULL,
        filing_date DATE NULL,
        accepted_at DATETIME NULL,
        available_at DATETIME NOT NULL,
        report_date DATE NULL,
        form_type VARCHAR(20) NULL,
        accession_no VARCHAR(32) NOT NULL,
        data_quality VARCHAR(20) NULL,
        is_audited TINYINT(1) NULL,
        is_restated TINYINT(1) NULL,
        is_estimated TINYINT(1) NULL,
        confidence DOUBLE NULL,

        source VARCHAR(20) NOT NULL DEFAULT 'edgar',
        last_collected_at TIMESTAMP NULL,
        error_msg TEXT NULL,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

        UNIQUE KEY uk_fin (symbol, freq, accession_no, statement_type, concept, period_end, unit),
        KEY ix_symbol (symbol),
        KEY ix_period_end (period_end),
        KEY ix_label (label),
        KEY ix_symbol_available_at (symbol, available_at),
        KEY ix_accession_no (accession_no),
        KEY ix_symbol_concept_available_at (symbol, statement_type, concept, available_at)
        );
    """,

    "financial_statement_labels":"""
        CREATE TABLE IF NOT EXISTS nyse_financial_statement_labels (
        symbol VARCHAR(20) NOT NULL,
        statement_type VARCHAR(50) NOT NULL,
        concept VARCHAR(255) NOT NULL,
        as_of DATE NOT NULL,
        label VARCHAR(255) NOT NULL,
        as_of_label VARCHAR(20) NULL,
        as_of_period_type ENUM('Q','FY','DATE') NULL,
        as_of_fiscal_year SMALLINT NULL,
        as_of_fiscal_quarter TINYINT NULL,

        label_kr VARCHAR(255) NULL,
        taxonomy VARCHAR(50) NULL,
        latest_unit VARCHAR(32) NULL,
        latest_filing_date DATE NULL,
        latest_accepted_at DATETIME NULL,
        latest_available_at DATETIME NULL,
        latest_accession_no VARCHAR(32) NULL,
        latest_form_type VARCHAR(20) NULL,
        confidence DOUBLE NULL,

        enabled TINYINT(1) NOT NULL DEFAULT 1,
        priority INT NULL,
        condition_json JSON NULL,

        last_updated_at TIMESTAMP NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

        PRIMARY KEY (symbol, statement_type, concept, as_of),
        KEY ix_label (label),
        KEY ix_symbol (symbol),
        KEY ix_as_of (as_of),
        KEY ix_symbol_available_at (symbol, latest_available_at)
        );
    """,

    "factors": """
        CREATE TABLE IF NOT EXISTS nyse_factors (
          id BIGINT AUTO_INCREMENT PRIMARY KEY,

          symbol VARCHAR(20) NOT NULL,
          freq   ENUM('annual','quarterly') NOT NULL,
          period_end DATE NOT NULL,

          price DOUBLE NULL,
          price_date DATE NULL,
          price_match_gap_days INT NULL,
          price_source VARCHAR(32) NOT NULL DEFAULT 'nyse_price_history',
          price_timeframe VARCHAR(10) NOT NULL DEFAULT '1d',
          timing_basis VARCHAR(32) NOT NULL DEFAULT 'period_end_asof',
          pit_mode VARCHAR(32) NOT NULL DEFAULT 'broad_research',
          market_cap BIGINT NULL,
          enterprise_value BIGINT NULL,

          psr DOUBLE NULL,
          sales_yield DOUBLE NULL,
          gpa DOUBLE NULL,
          por DOUBLE NULL,
          operating_income_yield DOUBLE NULL,
          ev_ebit DOUBLE NULL,
          per DOUBLE NULL,
          earnings_yield DOUBLE NULL,
          liquidation_value DOUBLE NULL,
          current_ratio DOUBLE NULL,
          cash_ratio DOUBLE NULL,
          pbr DOUBLE NULL,
          book_to_market DOUBLE NULL,
          debt_ratio DOUBLE NULL,
          debt_to_assets DOUBLE NULL,
          net_debt DOUBLE NULL,
          net_debt_to_equity DOUBLE NULL,
          pcr DOUBLE NULL,
          ocf_yield DOUBLE NULL,
          pfcr DOUBLE NULL,
          fcf_yield DOUBLE NULL,
          dividend_payout DOUBLE NULL,
          gross_margin DOUBLE NULL,
          operating_margin DOUBLE NULL,
          net_margin DOUBLE NULL,
          ocf_margin DOUBLE NULL,
          fcf_margin DOUBLE NULL,
          revenue_growth DOUBLE NULL,
          gross_profit_growth DOUBLE NULL,
          op_income_growth DOUBLE NULL,
          net_income_growth DOUBLE NULL,
          roe DOUBLE NULL,
          roa DOUBLE NULL,
          asset_turnover DOUBLE NULL,
          interest_coverage DOUBLE NULL,
          asset_growth DOUBLE NULL,
          debt_growth DOUBLE NULL,
          fcf_growth DOUBLE NULL,
          shares_growth DOUBLE NULL,

          last_calculated_at TIMESTAMP NULL,
          error_msg TEXT NULL,

          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

          UNIQUE KEY uk_symbol_freq_period (symbol, freq, period_end),
          KEY ix_symbol (symbol),
          KEY ix_period_end (period_end)
        );
    """,

    "factors_statement": """
        CREATE TABLE IF NOT EXISTS nyse_factors_statement (
          id BIGINT AUTO_INCREMENT PRIMARY KEY,

          symbol VARCHAR(20) NOT NULL,
          freq   ENUM('annual','quarterly') NOT NULL,
          period_end DATE NOT NULL,

          fundamental_available_at DATETIME NULL,
          fundamental_accession_no VARCHAR(32) NULL,

          price DOUBLE NULL,
          price_date DATE NULL,
          price_match_gap_days INT NULL,
          price_source VARCHAR(32) NOT NULL DEFAULT 'nyse_price_history',
          price_timeframe VARCHAR(10) NOT NULL DEFAULT '1d',
          timing_basis VARCHAR(48) NOT NULL DEFAULT 'latest_available_for_period_end',
          pit_mode VARCHAR(32) NOT NULL DEFAULT 'statement_derived_shadow',
          market_cap BIGINT NULL,
          enterprise_value BIGINT NULL,

          psr DOUBLE NULL,
          sales_yield DOUBLE NULL,
          gpa DOUBLE NULL,
          por DOUBLE NULL,
          operating_income_yield DOUBLE NULL,
          ev_ebit DOUBLE NULL,
          per DOUBLE NULL,
          earnings_yield DOUBLE NULL,
          liquidation_value DOUBLE NULL,
          current_ratio DOUBLE NULL,
          cash_ratio DOUBLE NULL,
          pbr DOUBLE NULL,
          book_to_market DOUBLE NULL,
          debt_ratio DOUBLE NULL,
          debt_to_assets DOUBLE NULL,
          net_debt DOUBLE NULL,
          net_debt_to_equity DOUBLE NULL,
          pcr DOUBLE NULL,
          ocf_yield DOUBLE NULL,
          pfcr DOUBLE NULL,
          fcf_yield DOUBLE NULL,
          dividend_payout DOUBLE NULL,
          gross_margin DOUBLE NULL,
          operating_margin DOUBLE NULL,
          net_margin DOUBLE NULL,
          ocf_margin DOUBLE NULL,
          fcf_margin DOUBLE NULL,
          revenue_growth DOUBLE NULL,
          gross_profit_growth DOUBLE NULL,
          op_income_growth DOUBLE NULL,
          net_income_growth DOUBLE NULL,
          roe DOUBLE NULL,
          roa DOUBLE NULL,
          asset_turnover DOUBLE NULL,
          interest_coverage DOUBLE NULL,
          asset_growth DOUBLE NULL,
          debt_growth DOUBLE NULL,
          fcf_growth DOUBLE NULL,
          shares_growth DOUBLE NULL,

          last_calculated_at TIMESTAMP NULL,
          error_msg TEXT NULL,

          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

          UNIQUE KEY uk_symbol_freq_period (symbol, freq, period_end),
          KEY ix_symbol (symbol),
          KEY ix_period_end (period_end),
          KEY ix_symbol_available_at (symbol, fundamental_available_at)
        );
    """
}
