{{ config(
    materialized='view',
    schema='intermediate'
) }}

WITH order_details AS (
    SELECT 
        o.order_id,
        o.customer_id,
        o.order_date,
        o.final_amount,
        o.quantity,
        p.category,
        p.product_name,
        p.gross_margin,
        (o.final_amount - (o.final_amount / (p.price + 0.01)) * p.cost) as profit
    FROM {{ ref('stg_orders') }} o
    LEFT JOIN {{ ref('stg_products') }} p ON o.product_id = p.product_id
)

SELECT 
    *,
    CASE 
        WHEN final_amount >= 1000 THEN 'High Value'
        WHEN final_amount >= 500 THEN 'Medium Value'
        ELSE 'Low Value'
    END as order_value_segment
FROM order_details
