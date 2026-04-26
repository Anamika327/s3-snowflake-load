{{ config(
    materialized='view',
    schema='staging'
) }}

SELECT 
    order_id,
    customer_id,
    product_id,
    order_date,
    amount,
    quantity,
    discount,
    CASE 
        WHEN discount > 0 THEN amount * (1 - discount)
        ELSE amount
    END as final_amount,
    created_at,
    _ingested_at
FROM {{ source('raw', 'orders') }}
WHERE order_id IS NOT NULL
    AND customer_id IS NOT NULL
    AND order_date IS NOT NULL
