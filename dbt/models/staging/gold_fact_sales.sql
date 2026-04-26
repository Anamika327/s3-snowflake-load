{{ config(
    materialized='table',
    schema='marts',
    tags=['gold', 'daily'],
    indexes=[
        {'columns': ['order_date'], 'type': 'hash'},
        {'columns': ['customer_id'], 'type': 'hash'},
        {'columns': ['category'], 'type': 'hash'}
    ]
) }}

WITH order_metrics AS (
    SELECT 
        o.order_id as sales_id,
        o.customer_id,
        o.order_date,
        o.final_amount as sale_amount,
        o.quantity,
        p.product_name,
        p.category,
        p.price,
        p.gross_margin,
        YEAR(o.order_date) as sales_year,
        MONTH(o.order_date) as sales_month,
        QUARTER(o.order_date) as sales_quarter,
        DAYOFWEEK(o.order_date) as sales_dayofweek,
        CURRENT_TIMESTAMP() as last_updated
    FROM {{ ref('stg_orders') }} o
    LEFT JOIN {{ ref('stg_products') }} p ON o.product_id = p.product_id
    WHERE o.order_date IS NOT NULL
)

SELECT 
    ROW_NUMBER() OVER (ORDER BY sales_id) as sales_key,
    *
FROM order_metrics
