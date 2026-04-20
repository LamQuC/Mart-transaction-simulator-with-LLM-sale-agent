{{ config(materialized='incremental', unique_key='sku_id||valid_from') }}

-- SCD Type 2: Lưu lịch sử thay đổi giá sản phẩm
with base as (
    select 
        sku_id,
        name,
        category,
        brand,
        cost_price,
        list_price,
        current_price,
        stock_quantity,
        description,
        now() as valid_from
    from {{ ref('stg_products') }}
)

select 
    sku_id,
    name,
    category,
    brand,
    cost_price,
    list_price,
    current_price,
    stock_quantity,
    description,
    valid_from,
    null::timestamp as valid_to
from base
