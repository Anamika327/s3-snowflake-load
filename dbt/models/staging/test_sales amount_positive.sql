-- Verify all sales amounts are positive
SELECT *
FROM {{ ref('gold_fact_sales') }}
WHERE sale_amount < 0
