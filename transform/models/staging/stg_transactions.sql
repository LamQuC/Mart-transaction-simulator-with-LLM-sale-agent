{{ config(materialized='view') }}

-- models/staging/stg_transactions.sql
SELECT 
    order_id,
    customer_id,
    customer_name,
    product_name,
    price,
    quantity,
    order_time,
    action_type,
    -- Logic: Nếu khách mua thì tính Doanh thu, nếu Supplier nhập thì tính Chi phí (50%)
    CASE 
        WHEN action_type = 'BUY' THEN (price * quantity) 
        ELSE 0 
    END as gross_revenue,
    CASE 
        WHEN action_type = 'RESTOCK' THEN (price * 0.5 * quantity) 
        ELSE 0 
    END as cost_amount
FROM {{ source('public', 'orders') }}