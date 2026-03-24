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
    
     "asset_profile": """
        CREATE TABLE IF NOT EXISTS nyse_asset_profile (
          id BIGINT AUTO_INCREMENT PRIMARY KEY,
          symbol VARCHAR(20) NOT NULL,
          kind   ENUM('stock','etf') NOT NULL,

          long_name VARCHAR(255) NULL,
          quote_type VARCHAR(20) NULL,

          sector   VARCHAR(100) NULL,
          industry VARCHAR(150) NULL,
          country  VARCHAR(50)  NULL,

          market_cap BIGINT NULL,
          dividend_yield DOUBLE NULL,
          payout_ratio   DOUBLE NULL,

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
