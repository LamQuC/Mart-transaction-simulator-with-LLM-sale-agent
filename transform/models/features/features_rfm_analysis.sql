{{ config(materialized='table') }}
-- RFM Analysis: Phân tích khách hàng theo Recency, Frequency, Monetary
with base as (
    select 
        customer_id,
        customer_name,
        max(order_time) as last_purchase,
        count(order_id) as frequency,
        sum(price * quantity - coalesce(discount_amount,0)) as monetary
    from {{ ref('stg_transactions') }}
    where action_type = 'BUY'
    group by customer_id, customer_name
),

rfm as (
    select 
        *,
        (select max(last_purchase) from base) as max_date
    from base
)

select 
    customer_id,
    customer_name,
    frequency,
    monetary,
    datediff('day', last_purchase, max_date) as recency
from rfm
order by monetary desc
