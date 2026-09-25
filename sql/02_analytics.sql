-- Średni kurs EUR w ostatnich 30 dniach
SELECT
    currency_code,
    ROUND(AVG(rate)::numeric, 4) AS avg_rate,
    MIN(rate) AS min_rate,
    MAX(rate) AS max_rate
FROM currency_rates
WHERE currency_code = 'EUR'
  AND effective_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY currency_code;

-- Kurs USD w ostatnich 10 dniach
SELECT
    effective_date,
    rate
FROM currency_rates
WHERE currency_code = 'USD'
ORDER BY effective_date DESC
LIMIT 10;