{{ config(
    materialized='table',
    schema='marts',
    tags=['gold', 'summary'],
    indexes=[
        {'columns': ['sales_date'], 'type': 'hash'}
    ]
) }}

SELECT 
    o.order_date as sales_date,
    COUNT(DISTINCT o.order_id) as total_transactions,
    COUNT(DISTINCT o.customer_id) as unique_customers,
    SUM(o.final_amount) as total_revenue,
    AVG(o.final_amount) as avg_transaction_value,
    MIN(o.final_amount) as min_order_value,
    MAX(o.final_amount) as max_order_value,
    SUM(o.quantity) as total_quantity_sold,
    CURRENT_TIMESTAMP() as last_updated
FROM {{ ref('stg_orders') }} o
GROUP BY o.order_date
ORDER BY o.order_date DESC
