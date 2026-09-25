-- Tabela kursów walut
CREATE TABLE IF NOT EXISTS currency_rates (
    id SERIAL PRIMARY KEY,
    currency_code VARCHAR(3) NOT NULL,
    currency_name VARCHAR(100) NOT NULL,
    rate NUMERIC(12, 6) NOT NULL,
    effective_date DATE NOT NULL,
    table_no VARCHAR(20),
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (currency_code, effective_date)
);

CREATE INDEX IF NOT EXISTS idx_rates_date ON currency_rates(effective_date);
CREATE INDEX IF NOT EXISTS idx_rates_currency ON currency_rates(currency_code);