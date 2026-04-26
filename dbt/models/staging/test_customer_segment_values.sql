-- Verify customer segments are valid
SELECT *
FROM {{ ref('gold_dim_customers') }}
WHERE customer_segment NOT IN ('VIP', 'Regular', 'Active', 'Inactive')
