-- Verify daily sales data is recent
SELECT *
FROM {{ ref('gold_summary_daily_sales') }}
WHERE sales_date < CURRENT_DATE() - 2
