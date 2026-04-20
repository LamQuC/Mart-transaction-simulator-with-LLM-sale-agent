{{ config(materialized='table') }}
-- Inventory Snapshot: Tồn kho cuối ngày
with daily_inventory as (
    select 
        date_trunc('day', order_time) as snapshot_date,
        product_name,
        sum(case when action_type = 'BUY' then -quantity when action_type = 'RESTOCK' then quantity else 0 end) as net_change
    from {{ ref('stg_transactions') }}
    group by 1, 2
),

cumulative as (
    select 
        product_name,
        snapshot_date,
        sum(net_change) over (partition by product_name order by snapshot_date) as inventory_level
    from daily_inventory
)

select 
    product_name,
    snapshot_date,
    inventory_level
from cumulative
order by product_name, snapshot_date
