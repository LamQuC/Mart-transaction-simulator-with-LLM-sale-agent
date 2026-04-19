{{ config(materialized='view') }}
-- Tạo features cho training ML: tổng chi tiêu, số lần mua, lần mua cuối cùng của mỗi khách hàng
select
    customer_id,
    customer_name,
    count(distinct order_id) as num_transactions,
    sum(quantity * price) as total_spent,
    max(order_time) as last_purchase_date
from {{ ref('int_transaction_details') }}
group by customer_id, customer_name
order by total_spent desc
