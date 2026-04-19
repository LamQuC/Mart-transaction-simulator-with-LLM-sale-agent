{{ config(materialized='view') }}

-- models/marts/mart_sales_summary.sql
SELECT
    date_trunc('hour', order_time) as period, -- Nhóm theo giờ 
    product_name,
    SUM(CASE WHEN action_type = 'BUY' THEN quantity ELSE 0 END) as total_sold_qty,
    SUM(gross_revenue) as total_revenue,
    SUM(cost_amount) as total_cost,
    SUM(gross_revenue - cost_amount) as net_profit -- Lợi nhuận ròng
FROM {{ ref('stg_transactions') }}
GROUP BY 1, 2
ORDER BY 1 DESC