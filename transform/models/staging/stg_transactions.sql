{{ config(materialized='view') }}
-- Lấy dữ liệu từ bảng orders (mô phỏng giao dịch thực tế)
select 
	order_id,
	customer_id,
	customer_name,
	product_name,
	price,
	quantity,
	order_time,
	action_type
from {{ source('public', 'orders') }}