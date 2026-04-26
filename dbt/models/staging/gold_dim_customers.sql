{{ config(
    materialized='table',
    schema='marts',
    tags=['gold', 'daily'],
    indexes=[
        {'columns': ['customer_id'], 'type': 'hash'},
        {'columns': ['customer_segment'], 'type': 'hash'}
    ]
) }}

WITH customer_base AS (
    SELECT 
        id as customer_id,
        name as customer_name,
        email,
        city,
        state,
        created_at
    FROM {{ ref('stg_customers') }}
),

customer_metrics AS (
    SELECT 
        c.customer_id,
        c.customer_name,
        c.email,
        c.city,
        c.state,
        COUNT(DISTINCT o.order_id) as total_orders,
        SUM(o.final_amount) as lifetime_value,
        AVG(o.final_amount) as avg_order_value,
        MAX(o.order_date) as last_order_date,
        MIN(o.order_date) as first_order_date,
        DATEDIFF('day', MAX(o.order_date), CURRENT_DATE()) as days_since_last_order,
        CASE 
            WHEN COUNT(DISTINCT o.order_id) >= 10 THEN 'VIP'
            WHEN COUNT(DISTINCT o.order_id) >= 5 THEN 'Regular'
            WHEN COUNT(DISTINCT o.order_id) >= 1 THEN 'Active'
            ELSE 'Inactive'
        END as customer_segment,
        c.created_at,
        CURRENT_TIMESTAMP() as last_updated
    FROM customer_base c
    LEFT JOIN {{ ref('stg_orders') }} o ON c.customer_id = o.customer_id
    GROUP BY c.customer_id, c.customer_name, c.email, c.city, c.state, c.created_at
)

SELECT 
    ROW_NUMBER() OVER (ORDER BY customer_id) as customer_key,
    *
FROM customer_metrics
