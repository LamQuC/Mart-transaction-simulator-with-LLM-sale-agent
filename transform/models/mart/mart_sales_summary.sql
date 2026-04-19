{{ config(materialized='table') }}
-- Tổng hợp doanh thu, số lượng bán theo ngày, cửa hàng, sản phẩm
select
    transaction_date,
    store_id,
    store_name,
    product_id,
    product_name,
    sum(quantity) as total_quantity,
    sum(quantity * price) as total_sales
from {{ ref('int_transaction_details') }}
group by transaction_date, store_id, store_name, product_id, product_name
order by transaction_date desc, total_sales desc
