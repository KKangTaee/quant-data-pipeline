# finance/data/db/schema.py

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

          quote_type VARCHAR(20) NULL,
          exchange   VARCHAR(20) NULL,
          exchange_name VARCHAR(50) NULL,

          sector   VARCHAR(100) NULL,
          industry VARCHAR(150) NULL,
          country  VARCHAR(50)  NULL,

          market_cap BIGINT NULL,
          dividend_yield DOUBLE NULL,
          payout_ratio   DOUBLE NULL,

          in_sp500       TINYINT(1) NULL,
          in_nasdaq100   TINYINT(1) NULL,
          in_russell2000 TINYINT(1) NULL,

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