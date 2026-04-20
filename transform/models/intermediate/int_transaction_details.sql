{{ config(materialized='view') }}
-- Join transactions with customers, products for richer context
select
    t.order_id,
    t.customer_id,
    t.customer_name,
    t.product_name,
    t.price,
    t.quantity,
    t.order_time,
    t.action_type,
    c.preference,
    c.patience
from {{ ref('stg_transactions') }} t
left join {{ ref('stg_customers') }} c on t.customer_id = c.customer_id
