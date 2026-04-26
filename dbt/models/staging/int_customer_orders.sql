{{ config(
    materialized='view',
    schema='intermediate'
) }}

WITH customer_orders AS (
    SELECT 
        c.customer_id,
        c.customer_name,
        o.order_id,
        o.order_date,
        o.final_amount,
        o.quantity,
        p.category,
        p.price,
        p.gross_margin,
        ROW_NUMBER() OVER (PARTITION BY c.customer_id ORDER BY o.order_date DESC) as recency_rank
    FROM {{ ref('stg_customers') }} c
    LEFT JOIN {{ ref('stg_orders') }} o ON c.id = c.customer_id
    LEFT JOIN {{ ref('stg_products') }} p ON o.product_id = p.product_id
)

SELECT 
    customer_id,
    customer_name,
    order_id,
    order_date,
    final_amount,
    quantity,
    category,
    price,
    gross_margin,
    recency_rank
FROM customer_orders
